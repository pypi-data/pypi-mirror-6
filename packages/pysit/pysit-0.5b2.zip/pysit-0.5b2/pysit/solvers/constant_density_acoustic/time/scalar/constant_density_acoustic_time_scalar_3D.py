import numpy as np
import scipy.sparse as spsp

from pysit.solvers.wavefield_vector import *
from constant_density_acoustic_time_scalar_base import *

from pysit.util import Bunch
from pysit.util.derivatives import build_derivative_matrix
from pysit.util.matrix_helpers import build_sigma, make_diag_mtx

from constant_density_acoustic_time_scalar_cpp import *

__all__=['ConstantDensityAcousticTimeScalar_3D']

__docformat__ = "restructuredtext en"
		
class ConstantDensityAcousticTimeScalar_3D(ConstantDensityAcousticTimeScalarBase):
	
	@property #getter
	def cpp_accelerated(self): return True
		
	_cpp_funcs = { 2 : constant_density_acoustic_time_scalar_3D_2os,
	               4 : constant_density_acoustic_time_scalar_3D_4os,
	               6 : constant_density_acoustic_time_scalar_3D_6os,
	               8 : constant_density_acoustic_time_scalar_3D_8os,
	             }
	
	def __init__(self, mesh, **kwargs):
		
		self.operator_components = Bunch()
		
		ConstantDensityAcousticTimeScalarBase.__init__(self, mesh, **kwargs)

	def _rebuild_operators(self):
		
		dof = self.mesh.dof(include_bc=True)
		
		oc = self.operator_components
		# Check if empty.  If empty, build the static components
		if not self.operator_components: 
			# build laplacian
			oc.L = build_derivative_matrix(self.mesh, 2, self.spatial_accuracy_order, use_shifted_differences=self.spatial_shifted_differences)
			
			# build sigmax
			sx = build_sigma(self.mesh, self.mesh.x)
			oc.sigmax = make_diag_mtx(sx)
			
			# build sigmay
			sy = build_sigma(self.mesh, self.mesh.y)
			oc.sigmay = make_diag_mtx(sy)
			
			# build sigmaz 
			sz = build_sigma(self.mesh, self.mesh.z)
			oc.sigmaz = make_diag_mtx(sz)
			
			# build Dx
			oc.minus_Dx = build_derivative_matrix(self.mesh, 1, self.spatial_accuracy_order, dimension='x', use_shifted_differences=self.spatial_shifted_differences)
			oc.minus_Dx.data *= -1
			
			# build Dy
			oc.minus_Dy = build_derivative_matrix(self.mesh, 1, self.spatial_accuracy_order, dimension='y', use_shifted_differences=self.spatial_shifted_differences)
			oc.minus_Dy.data *= -1
			
			# build Dz
			oc.minus_Dz = build_derivative_matrix(self.mesh, 1, self.spatial_accuracy_order, dimension='z', use_shifted_differences=self.spatial_shifted_differences)
			oc.minus_Dz.data *= -1
			
			# build other useful things
			oc.I       = spsp.eye(dof,dof)
			oc.minus_I = -1*oc.I
			oc.empty   = spsp.csr_matrix((dof,dof))
			
			# useful intermediates
			oc.sigma_sum_pair_prod  = make_diag_mtx((sx*sy+sx*sz+sy*sz))
			oc.sigma_sum            = make_diag_mtx((sx+sy+sz))
			oc.sigma_prod           = make_diag_mtx(sx*sy*sz)
			oc.minus_sigma_yPzMx_Dx = make_diag_mtx(sy+sz-sx)*oc.minus_Dx
			oc.minus_sigma_xPzMy_Dy = make_diag_mtx(sx+sz-sy)*oc.minus_Dy
			oc.minus_sigma_xPyMz_Dz = make_diag_mtx(sx+sy-sz)*oc.minus_Dz
			
			oc.minus_sigma_yz_Dx    = make_diag_mtx(sy*sz)*oc.minus_Dx
			oc.minus_sigma_zx_Dy    = make_diag_mtx(sz*sx)*oc.minus_Dy
			oc.minus_sigma_xy_Dz    = make_diag_mtx(sx*sy)*oc.minus_Dz
			
		C = self.model_parameters.C # m = self.model_parameters.M[0]
		oc.m = make_diag_mtx((C**-2).reshape(-1,))
		
		K = spsp.bmat([[oc.m*oc.sigma_sum_pair_prod-oc.L, oc.m*oc.sigma_prod,   oc.minus_Dx, oc.minus_Dy, oc.minus_Dz ],
		               [oc.minus_I,                       oc.empty,             oc.empty,    oc.empty,    oc.empty    ],
                       [oc.minus_sigma_yPzMx_Dx,          oc.minus_sigma_yz_Dx, oc.sigmax,   oc.empty,    oc.empty    ],
                       [oc.minus_sigma_xPzMy_Dy,          oc.minus_sigma_zx_Dy, oc.empty,    oc.sigmay,   oc.empty    ],
                       [oc.minus_sigma_xPyMz_Dz,          oc.minus_sigma_xy_Dz, oc.empty,    oc.empty,    oc.sigmaz   ]])
                       
		C = spsp.bmat([[oc.m*oc.sigma_sum, oc.empty, oc.empty, oc.empty, oc.empty],           
			           [oc.empty,          oc.I,     oc.empty, oc.empty, oc.empty],           
			           [oc.empty,          oc.empty, oc.I,     oc.empty, oc.empty],           
			           [oc.empty,          oc.empty, oc.empty, oc.I,     oc.empty],           
			           [oc.empty,          oc.empty, oc.empty, oc.empty, oc.I    ]]) / self.dt
		
		M = spsp.bmat([[    oc.m, oc.empty, oc.empty, oc.empty, oc.empty],
			           [oc.empty, oc.empty, oc.empty, oc.empty, oc.empty],
			           [oc.empty, oc.empty, oc.empty, oc.empty, oc.empty],
			           [oc.empty, oc.empty, oc.empty, oc.empty, oc.empty],
			           [oc.empty, oc.empty, oc.empty, oc.empty, oc.empty]]) / self.dt**2
			           
		Stilde_inv = M+C
		Stilde_inv.data = 1./Stilde_inv.data 
			
		self.A_k   = Stilde_inv*(2*M - K + C)
		self.A_km1 = -1*Stilde_inv*(M)
		self.A_f   = Stilde_inv
	
	def _time_step_accelerated(self, solver_data, rhs_k, rhs_kp1):
		
		lpmlx = self.mesh.x.lbc.sigma if self.mesh.x.lbc.type is 'pml' else np.array([])
		rpmlx = self.mesh.x.rbc.sigma if self.mesh.x.rbc.type is 'pml' else np.array([])
		
		lpmly = self.mesh.y.lbc.sigma if self.mesh.y.lbc.type is 'pml' else np.array([])
		rpmly = self.mesh.y.rbc.sigma if self.mesh.y.rbc.type is 'pml' else np.array([])
		
		lpmlz = self.mesh.z.lbc.sigma if self.mesh.z.lbc.type is 'pml' else np.array([])
		rpmlz = self.mesh.z.rbc.sigma if self.mesh.z.rbc.type is 'pml' else np.array([])
		
		nx,ny,nz = self.mesh.shape(include_bc=True, as_grid=True)
		
		self._cpp_funcs[self.spatial_accuracy_order](solver_data.km1.u,
		                                            solver_data.k.Phix,
		                                            solver_data.k.Phiy,
		                                            solver_data.k.Phiz,
		                                            solver_data.k.psi,
		                                            solver_data.k.u,
		                                            self.model_parameters.C,
		                                            rhs_k,
		                                            lpmlx, rpmlx,
		                                            lpmly, rpmly,
		                                            lpmlz, rpmlz,
		                                            self.dt,
		                                            self.mesh.x.delta,
		                                            self.mesh.y.delta,
		                                            self.mesh.z.delta,
		                                            nx, ny, nz,
		                                            solver_data.kp1.Phix,
		                                            solver_data.kp1.Phiy,
		                                            solver_data.kp1.Phiz,
		                                            solver_data.kp1.psi,
		                                            solver_data.kp1.u
		                                            )
		
	class WavefieldVector(WavefieldVectorBase):
		
		aux_names = ['psi', 'Phix', 'Phiy', 'Phiz']