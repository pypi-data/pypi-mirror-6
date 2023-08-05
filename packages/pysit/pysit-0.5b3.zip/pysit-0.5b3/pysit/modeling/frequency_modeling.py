from __future__ import absolute_import

import itertools

import numpy as np

__all__ = ['FrequencyModeling']

__docformat__ = "restructuredtext en"

class FrequencyModeling(object):

	# read only class description
	@property
	def solver_type(self): return "frequency"
	@property
	def modeling_type(self): return "frequency"
		
	def __init__(self, solver):
		"""Constructor for the FrequencyInversion class.
		
		Parameters
		----------
		solver : pysit wave solver object
			A wave solver that inherits from pysit.solvers.WaveSolverBase
		 
		"""
		if self.solver_type == solver.solver_type:
			self.solver = solver
		else:
			raise TypeError("Argument 'solver' type {1} does not match modeling solver type {0}.".format(self.solver_type, solver.solver_type))

	def forward_model(self, shot, m0, frequencies, return_parameters=[]):
		"""Applies the forward model to the model for the given solver.
		
		Parameters
		----------
		shot : pysit.Shot
			Gives the source signal approximation for the right hand side.
		frequencies : list of 2-tuples
			2-tuple, first element is the frequency to use, second element the weight.
		return_parameters : list of {'wavefield', 'simdata', 'simdata_time', 'dWaveOp'}
		
		Returns
		-------
		retval : dict
			Dictionary whose keys are return_parameters that contains the specified data.
		
		Notes
		-----
		* u is used as the target field universally.  It could be velocity potential, it could be displacement, it could be pressure.  
		* uhat is used to generically refer to the DFT of u that is needed to compute the imaging condition.
		
		"""
	
		# Local references
		solver = self.solver
		solver.model_parameters = m0 # this updates dt and the number of steps so that is appropriate for the current model
		
		mesh = solver.mesh
		
		d = solver.domain
		source = shot.sources

		# Sanitize the input
		if not np.iterable(frequencies):
			frequencies = [frequencies]		
		
		# Setup data storage for the forward modeled data
		if 'simdata' in return_parameters:
			simdata = dict()
	
		# Storage for the derivative of the propagation operator with respect to the model \frac{d\script{L}}{dm}
		if 'dWaveOp' in return_parameters:
			dWaveOp = dict()
				
		# Initialize the DFT components
		uhats = dict()
			
		
		# Step k = 0
		# p_0 is a zero array because if we assume the input signal is causal
		# and we assume that the initial system (i.e., p_(-2) and p_(-1)) is
		# uniformly zero, then the leapfrog scheme would compute that p_0 = 0 as
		# well. ukm1 is needed to compute the temporal derivative.
		
		solver_data = solver.SolverData()
		rhs = solver.WavefieldVector(mesh,dtype=solver.dtype)
		for nu in frequencies:
			rhs = solver.build_rhs(mesh.pad_array(source.f(nu=nu)), rhs_wavefieldvector=rhs)
			result = solver.solve(solver_data, rhs, nu)
			uhat = solver_data.k.primary_wavefield
			
			# Save the unpadded wavefield
			if 'wavefield' in return_parameters:
				uhats[nu] = mesh.unpad_array(uhat, copy=True)
			
			# Record the data at t_k
			if 'simdata' in return_parameters:
					simdata[nu] = shot.receivers.sample_data_from_array(mesh.unpad_array(uhat))
			
			# Save the derivative		
			if 'dWaveOp' in return_parameters:
				dWaveOp[nu] = solver.compute_dWaveOp('frequency', uhat, nu)
			
		retval = dict()
		
		if 'dWaveOp' in return_parameters:
			retval['dWaveOp'] = dWaveOp
		if 'simdata' in return_parameters:
			retval['simdata'] = simdata
		if 'wavefield' in return_parameters:
			retval['wavefield'] = uhats
			
		return retval

	def migrate_shot(self, shot, m0, operand_simdata, frequencies,
		                   operand_dWaveOpAdj=None, operand_model=None, 
	                       frequency_weights=None, 
	                       dWaveOp=None,
	                       adjointfield=None, dWaveOpAdj=None):
		"""Performs migration on a single shot.
		
		Parameters
		----------
		shot : pysit.Shot
			Shot for which to compute migration.
		operand_simdata : ndarray
			Operand, i.e., b in F*b. This data is in TIME to properly compute the adjoint.
		frequencies : list of 2-tuples
			2-tuple, first element is the frequency to use, second element the weight.
		utt : list
			Imaging condition components from the forward model for each receiver in the shot.
		qs : list
			Optional return list allowing us to retrieve the adjoint field as desired.
		 
		"""
		
		# If the imaging component has not already been computed, compute it.
		prep_rp = list()
		if dWaveOp is None:
			prep_rp.append('dWaveOp')
			dWaveOp = dict()
				
		if len(prep_rp) > 0:
			retval = self.forward_model(shot, m0, frequencies, return_parameters=prep_rp)
			if 'dWaveOp' in prep_rp:
				dWaveOp = retval['dWaveOp']
		
		rp = ['imaging_condition']
		if adjointfield is not None: 
			rp.append('adjointfield')
		if dWaveOpAdj is not None:
			rp.append('dWaveOpAdj')
		
		rv = self.adjoint_model(shot, m0, operand_simdata, frequencies, operand_dWaveOpAdj=operand_dWaveOpAdj, operand_model=operand_model, frequency_weights=frequency_weights, return_parameters=rp, dWaveOp=dWaveOp)
		
		# If the adjoint field is desired as output.
		for nu in frequencies:
			if adjointfield is not None:
				adjointfield[nu] = rv['adjointfield'][nu]
			if dWaveOpAdj is not None:
				dWaveOpAdj[nu] = rv['dWaveOpAdj'][nu]
		
		# Get the imaging condition part from the result, this is the migrated image.
		ic = rv['imaging_condition']
		
		return ic
		
	def adjoint_model(self, shot, m0,
	                       operand_simdata, frequencies,
	                       operand_dWaveOpAdj=None, operand_model=None,
	                       frequency_weights=None, 
	                       return_parameters=[], 
	                       dWaveOp=None):
		"""Solves for the adjoint field in frequency.
		
		m*q_tt - lap q = resid
		
		Parameters
		----------
		shot : pysit.Shot
			Gives the receiver model for the right hand side.
		operand : ndarray
			Right hand side, usually the residual.
		frequencies : list of 2-tuples
			2-tuple, first element is the frequency to use, second element the weight.
		return_parameters : list of {'q', 'qhat', 'ic'}
		dWaveOp : ndarray
			Imaging component from the forward model (in frequency).
			
		Returns
		-------
		retval : dict
			Dictionary whose keys are return_parameters that contains the specified data.
		
		Notes
		-----
		* q is the adjoint field.
		* qhat is the DFT of oq at the specified frequencies
		* ic is the imaging component.  Because this function computes many of 
		the things required to compute the imaging condition, there is an option 
		to compute the imaging condition as we go.  This should be used to save 
		computational effort.  If the imaging condition is to be computed, the
		optional argument utt must be present.
		
		"""
		
		# Sanitize the input
		if not np.iterable(frequencies):
			frequencies = [frequencies]	
		
		# Local references	
		solver = self.solver
		solver.model_parameters = m0
		
		mesh = solver.mesh
		
		d = solver.domain
		source = shot.sources
		
		# Sanitize the input
		if not np.iterable(frequencies):
			frequencies = [frequencies]	
				
		qhats = dict()
		
		if 'dWaveOpAdj' in return_parameters:
			dWaveOpAdj = dict()
			
		# If we are computing the imaging condition, ensure that all of the parts are there.
		if dWaveOp is None and 'imaging_condition' in return_parameters:
			raise ValueError('To compute imaging condition, forward component must be specified.')

		if 'imaging_condition' in return_parameters:
			ic = solver.model_parameters.perturbation(dtype=np.complex)
			
			if frequency_weights is None:
				frequency_weights = itertools.repeat(1.0)
			
			freq_weights = {nu: weight for nu,weight in zip(frequencies,frequency_weights)}
				
		if operand_model is not None:
			operand_model = operand_model.with_padding()
				
		# Time-reversed wave solver
		solver_data = solver.SolverData()
		rhs = solver.WavefieldVector(mesh,dtype=solver.dtype)
		for nu in frequencies:
			# Compute the rhs array.
			
			rhs_ = mesh.pad_array(shot.receivers.extend_data_to_array(data=operand_simdata[nu])) # for primary adjoint equation
			if (operand_dWaveOpAdj is not None) and (operand_model is not None):
				dWaveOpAdj_nu = operand_dWaveOpAdj[nu]
				rhs_ += reshape(operand_model*dWaveOpAdj_nu.reshape(operand_model.shape), rhs_.shape) # for secondary adjoint equation
				
			rhs = solver.build_rhs(rhs_, rhs_wavefieldvector=rhs)
			
			np.conj(rhs.data, rhs.data)		
			result = solver.solve(solver_data, rhs, nu)
			
			vhat = solver_data.k.primary_wavefield
			# Compute the conjugate in place.
			# After this operation, vhats _is_ conjugated, so its value does not
			# match the mathematics.  This is done to save computation, as computing
			# the conjufation in place requires no further allocation.  vhats should
			# not be used beyond this point, so it is assigned to None.
			qhat = np.conj(vhat, vhat)
			
			if 'adjointfield' in return_parameters:
				qhats[nu] = mesh.unpad_array(qhat, copy=True)
				
			if 'dWaveOpAdj' in return_parameters:
				dWaveOpAdj[nu] = solver.compute_dWaveOp('frequency', qhat,nu)
				
			# If the imaging component needs to be computed, do it
			if 'imaging_condition' in return_parameters:
				weight = freq_weights[nu]
				ic -= weight*qhat*np.conj(dWaveOp[nu]) # note, no dnu here because the nus are not generally the complete set, so dnu makes little sense, otherwise dnu = 1./(nsteps*dt)
			
		retval = dict()
		
		if 'adjointfield' in return_parameters:
			retval['adjointfield'] = qhats
			
		if 'dWaveOpAdj' in return_parameters:
			retval['dWaveOpAdj'] = dWaveOpAdj
		
		# If the imaging component needs to be computed, do it
		if 'imaging_condition' in return_parameters:
			retval['imaging_condition'] = ic.without_padding() 
		
		return retval

	def linear_forward_model(self, shot, m0, m1, frequencies, return_parameters=[], dWaveOp0=None):
		"""Applies the forward model to the model for the given solver.
		
		Parameters
		----------
		shot : pysit.Shot
			Gives the source signal approximation for the right hand side.
		m1 : solver.ModelParameters
		frequencies : list of 2-tuples
			2-tuple, first element is the frequency to use, second element the weight.
		return_parameters : list of {'dWaveOp0', 'wavefield1', 'dWaveOp1', 'simdata', 'simdata_time'}, optional
			Values to return.
		
		
		Returns
		-------
		retval : dict
			Dictionary whose keys are return_parameters that contains the specified data.
		
		Notes
		-----
		* u1 is used as the target field universally.  It could be velocity potential, it could be displacement, it could be pressure.  
		* u1tt is used to generically refer to the derivative of u1 that is needed to compute the imaging condition.
		* If u0tt is not specified, it may be computed on the fly at potentially high expense.
		
		"""

		# Sanitize the input
		if not np.iterable(frequencies):
			frequencies = [frequencies]	
			
		# Local references
		solver = self.solver
		solver.model_parameters = m0 # this updates dt and the number of steps so that is appropriate for the current model
		
		mesh = solver.mesh
		
		d = solver.domain
		source = shot.sources

		m1_padded = m1.with_padding()
		
		# Storage for the field		
		u1hats = dict()
		
		# Setup data storage for the forward modeled data
		if 'simdata' in return_parameters:
			simdata = dict()

		# Storage for the time derivatives of p
		if 'dWaveOp0' in return_parameters:
			dWaveOp0ret = dict()

		# Storage for the time derivatives of p
		if 'dWaveOp1' in return_parameters:
			dWaveOp1 = dict()
				
		if dWaveOp0 is None:
			solver_data_u0 = solver.SolverData()
			
		solver_data = solver.SolverData()
		
		rhs = solver.WavefieldVector(mesh,dtype=solver.dtype)
		
		for nu in frequencies:
			if dWaveOp0 is None:
				rhs = solver.build_rhs(mesh.pad_array(source.f(nu=nu)), rhs_wavefieldvector=rhs)
				solver.solve(solver_data_u0, rhs, nu)
				u0hat = solver_data_u0.k.primary_wavefield
				dWaveOp0_nu = solver.compute_dWaveOp('frequency', u0hat, nu)
			else:
				dWaveOp0_nu = dWaveOp0[nu]
				
			if 'dWaveOp0' in return_parameters:
				dWaveOp0ret[nu] = dWaveOp0_nu
			
			rhs_ = m1_padded*(-1*dWaveOp0_nu)
			rhs = solver.build_rhs(rhs_, rhs_wavefieldvector=rhs) # make the rhs vector the correct length
			solver.solve(solver_data,rhs,nu)
			
			u1hat = solver_data.k.primary_wavefield
			
			# Store the wavefield
			if 'wavefield1' in return_parameters:
				u1hats[nu] = mesh.unpad_array(u1hat, copy=True)
			
			# Compute the derivative
			if 'dWaveOp1' in return_parameters:
				dWaveOp1[nu] = solver.compute_dWaveOp('frequency', u1hat, nu)
			
			# Extract the data
			if 'simdata' in return_parameters:
				simdata[nu] = shot.receivers.sample_data_from_array(mesh.unpad_array(u1hat))

		retval = dict()
		
		if 'dWaveOp0' in return_parameters:
			retval['dWaveOp0'] = dWaveOp0ret
		if 'wavefield1' in return_parameters:
			retval['wavefield1'] = u1hats
		if 'dWaveOp1' in return_parameters:
			retval['dWaveOp1'] = dWaveOp1
		if 'simdata' in return_parameters:
			retval['simdata'] = simdata
		
		return retval

def adjoint_test():
#if __name__ == '__main__':
#	from pysit import *
	import numpy as np
	import matplotlib.pyplot as plt
	
	from pysit import PML, Dirichlet, RectangularDomain, CartesianMesh, PointSource, ReceiverSet, Shot, ConstantDensityAcousticWave,ConstantDensityHelmholtz, generate_seismic_data, PointReceiver, RickerWavelet
	from pysit.gallery import horizontal_reflector

	#	Define Domain
	bc = PML(0.3, 100, ftype='quadratic')
#	bc = Dirichlet()
	
	x_config = (0.1, 1.0, bc, bc)
	z_config = (0.1, 0.8, bc, bc)

	d = RectangularDomain( x_config, z_config )
	
	m = CartesianMesh(d, 90, 70)

	#	Generate true wave speed
	#   (M = C^-2 - C0^-2)
	C0, C = horizontal_reflector(m)

	# Set up shots
	Nshots = 1
	shots = []
	
	xmin = d.x.lbound
	xmax = d.x.rbound
	nx   = m.x.n
	zmin = d.z.lbound
	zmax = d.z.rbound
	
	point_approx = 'delta'
	
	for i in xrange(Nshots):

		# Define source location and type
		source = PointSource(m, (.188888, 0.18888), RickerWavelet(10.0), approximation=point_approx)
	
		# Define set of receivers
		zpos = zmin + (1./9.)*zmax
		xpos = np.linspace(xmin, xmax, nx)
		receivers = ReceiverSet(m, [PointReceiver(m, (x, zpos)) for x in xpos])
	
		# Create and store the shot
		shot = Shot(source, receivers)
		shots.append(shot)
	
	# Define and configure the wave solver
	trange=(0.,3.0)
	solver = ConstantDensityAcousticWave(m, 
	                                     formulation='scalar',
	                                     model_parameters={'C': C}, 
		                                 spatial_accuracy_order=4,
		                                 trange=trange,
		                                 time_accuracy_order=6)
	
	# Generate synthetic Seismic data
	print('Generating data...')
	base_model = solver.ModelParameters(m,{'C': C})
	generate_seismic_data(shots, solver, base_model)
	
	solver_frequency = ConstantDensityHelmholtz(m,
	                                            model_parameters={'C': C0},
		                                        spatial_shifted_differences=True,
	                                            spatial_accuracy_order=4)
	tools = FrequencyModeling(solver_frequency)
	m0 = solver_frequency.ModelParameters(m,{'C': C0})
	
	np.random.seed(0)
	
	m1 = m0.perturbation() 
#	m1 += M
	m1  += np.random.rand(*m1.data.shape)
	
	freqs = [10.0, 10.5, 10.123334145252]
#	freqs = np.linspace(3,20,20)
		
	fwdret = tools.forward_model(shot, m0, freqs, ['wavefield', 'dWaveOp', 'simdata'])
	data = fwdret['simdata']
	dWaveOp0 = fwdret['dWaveOp']
	u0hat = fwdret['wavefield'][freqs[0]]

#	data -= shot.receivers.interpolate_data(solver.ts())
#	data *= -1	

#	for nu in freqs:
#		data[nu] += np.random.rand(*data[nu].shape)
		
	linfwdret = tools.linear_forward_model(shot, m0, m1, freqs, ['simdata','wavefield1'])
	lindata = linfwdret['simdata']
	u1hat = linfwdret['wavefield1'][freqs[0]]
	
	adjret = tools.adjoint_model(shot, m0, data, freqs, return_parameters=['imaging_condition', 'adjointfield'], dWaveOp=dWaveOp0)
	qhat = adjret['adjointfield'][freqs[0]]
	adjmodel = adjret['imaging_condition'].data
	
#	adjret2 = tools.adjoint_model(shot, m0, lindata_time, freqs, return_parameters=['imaging_condition', 'adjointfield'], dWaveOp=dWaveOp0)
##	qhat = adjret['adjointfield'][freqs[0]]
#	adjmodel2 = adjret2['imaging_condition'].view(np.ndarray)

	m1 = m1.data
	
	temp_data_prod = 0.0
	for nu in freqs:
		temp_data_prod += np.dot(lindata[nu].reshape(data[nu].shape).T, np.conj(data[nu]))
	
	print temp_data_prod.squeeze()
	print np.dot(m1.T, np.conj(adjmodel)).squeeze()*np.prod(m.deltas)
	print np.dot(m1.T, np.conj(adjmodel)).squeeze()*np.prod(m.deltas) - temp_data_prod.squeeze()
	
#	temp_data_prod = 0.0
#	for nu in freqs:
#		temp_data_prod += np.dot(lindata[nu].reshape(dhat[nu].shape), np.conj(lindata[nu].reshape(dhat[nu].shape)))
#	
#	print temp_data_prod
#	print np.dot(m1.T, np.conj(adjmodel2)).squeeze()*np.prod(d.deltas)

#	plt.figure()
#	plt.subplot(2,3,1)
#	display_on_grid(np.real(u0hat), d)
#	plt.title(r're(${\hat u_0}$)')
#	plt.subplot(2,3,4)
#	display_on_grid(np.imag(u0hat), d)
#	plt.title(r'im(${\hat u_0}$)')
#	plt.subplot(2,3,2)
#	display_on_grid(np.real(qhat), d)
#	plt.title(r're(${\hat q}$)')
#	plt.subplot(2,3,5)
#	display_on_grid(np.imag(qhat), d)
#	plt.title(r'im(${\hat q}$)')
#	plt.subplot(2,3,3)
#	display_on_grid(np.real(u1hat), d)
#	plt.title(r're(${\hat u_1}$)')
#	plt.subplot(2,3,6)
#	display_on_grid(np.imag(u1hat), d)
#	plt.title(r'im(${\hat u_1}$)')
#	plt.show()

#	plt.figure()
#	plt.subplot(2,3,1)
#	display_on_grid(np.real(u0hat), d)
#	plt.title(r're(${\hat u_0}$)')
#	plt.subplot(2,3,4)
#	display_on_grid(np.imag(u0hat), d)
#	plt.title(r'im(${\hat u_0}$)')
#	plt.subplot(2,3,2)
#	display_on_grid(np.real(qhat), d)
#	plt.title(r're(${\hat q}$)')
#	plt.subplot(2,3,5)
#	display_on_grid(np.imag(qhat), d)
#	plt.title(r'im(${\hat q}$)')
#	plt.subplot(2,3,3)
#	display_on_grid(np.real(adjmodel), d)
#	plt.title(r're(${m_1}$)')
#	plt.subplot(2,3,6)
#	display_on_grid(np.imag(adjmodel), d)
#	plt.title(r'im(${m_1}$)')
#	plt.show()

if __name__ == '__main__':
	
	adjoint_test()