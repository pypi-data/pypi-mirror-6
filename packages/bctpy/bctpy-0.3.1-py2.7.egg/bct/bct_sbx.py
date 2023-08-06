#	(C) Roan LaPlante 2013 rlaplant@nmr.mgh.harvard.edu
#
#	This program is BCT-python, the Brain Connectivity Toolbox for python.
#
#	BCT-python is based on BCT, the Brain Connectivity Toolbox.  BCT is the
# 	collaborative work of many contributors, and is maintained by Olaf Sporns
#	and Mikail Rubinov.  For the full list, see the associated contributors.
#
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division
import numpy as np
import bct

def comodularity_und(a1,a2):
	'''
	Returns the comodularity, an experimental measure I am developing.
	The comodularity evaluates the correspondence between two community
	structures A and B.  Let F be the set of nodes that are co-modular (in the
	same module) in at least one of these community structures.  Let f be the
	set of nodes that are co-modular in both of these community structures.
	The comodularity is |f|/|F|
	'''

	ma,qa=bct.modularity_und(a1)
	mb,qb=bct.modularity_und(a2)

	n=len(ma)
	if len(mb)!=n:
		raise bct.BCTParamError('Comodularity must be done on equally sized '
			'matrices')

	E,F,f,G,g,H,h=(0,)*7

	for e1 in xrange(n):
		for e2 in xrange(n):
			if e2>=e1: continue

			#node pairs
			comod_a = ma[e1]==ma[e2] 
			comod_b = mb[e1]==mb[e2]

			#node pairs sharing a module in at least one graph
			if comod_a or comod_b:
				F+=1
			#node pairs sharing a module in both graphs
			if comod_a and comod_b:
				f+=1

			#edges in either graph common to any module
			if a1[e1,e2] != 0 or a2[e1,e2] != 0:
				#edges that exist in at least one graph which prepend a shared
				#module in at least one graph:
				#EXTREMELY NOT USEFUL SINCE THE SHARED MODULE MIGHT BE THE OTHER
				#GRAPH WITH NO EDGE!
				if comod_a or comod_b:
					G+=1
				#edges that exist in at least one graph which prepend a shared
				#module in both graphs:
				if comod_a and comod_b:
					g+=1

				#edges that exist at all
				E+=1

			#edges common to a module in both graphs
			if a1[e1,e2] != 0 and a2[e1,e2] != 0:
				#edges that exist in both graphs which prepend a shared module
				#in at least one graph
				if comod_a or comod_b:
					H+=1
				#edges that exist in both graphs which prepend a shared module
				#in both graphs
				if comod_a and comod_b:
					h+=1


	m1 = np.max(ma)
	m2 = np.max(mb)
	P=m1+m2-1

	#print f,F
	print m1,m2
	print 'f/F', f/F
	print '(f/F)*p', f*P/F
	print 'g/E', g/E
	print '(g/E)*p', g*P/E
	print 'h/E', h/E
	print '(h/E)*p', h*P/E
	print 'h/H', h/H
	print '(h/H)*p', h*P/E
	print 'q1, q2', qa, qb
	#print 'f/F*sqrt(qa*qb)', f*np.sqrt(qa*qb)/F
	return f/F

def comod_test(a1,a2):
	ma,qa=bct.modularity_und(a1)
	mb,qb=bct.modularity_und(a2)

	n=len(ma)
	if len(mb)!=n:
		raise BCTParamError('Comodularity must be done on equally sized '
			'matrices')

	f,F=(0,)*2

	for e1 in xrange(n):
		for e2 in xrange(n):
			if e2>=e1: continue

			#node pairs
			comod_a = ma[e1]==ma[e2] 
			comod_b = mb[e1]==mb[e2]

			#node pairs sharing a module in at least one graph
			if comod_a or comod_b:
				F+=1
			#node pairs sharing a module in both graphs
			if comod_a and comod_b:
				f+=1

	m1=np.max(ma)
	m2=np.max(mb)
	eta=[]
	gamma=[]
	for i in xrange(m1):
		eta.append(np.size(np.where(ma==i+1)))
	for i in xrange(m2):
		gamma.append(np.size(np.where(mb==i+1)))

	scale,conscale = (0,)*2
	for h in eta:
		for g in gamma:
			#print h,g
			conscale += (h*g)/(n*(h+g)-h*g)
			scale+= (h*h*g*g)/(n**3*(h+g)-n*h*g)

	print m1,m2
#	print conscale
	print scale
	return (f/F)/scale

def cross_modularity(a1,a2):
	ma,qa=bct.modularity_und(a1)
	mb,qb=bct.modularity_und(a2)

	_,qab=bct.modularity_und(a1,kci=mb)
	_,qba=bct.modularity_und(a2,kci=ma)

	#print 'A-A*',qab
	#print 'B-B*',qba

	return (qab+qba)/(qa+qb)

def nonparametric_similarity_test(similarity_metric,a1,a2,nshuff=1000):
	true_similarity = similarity_metric(a1,a2)	

	count=0.
	for shuff in xrange(1,nshuff+1):
		flip = np.random.random() > .5
		if flip:
			#a1_surr,_ = bct.null_model_und_sign(a1,bin_swaps=0)
			a1_surr = bct.randmio_und(a1, 1)[0]
			a2_surr = a2
		else:
			a1_surr = a1
			a2_surr = bct.randmio_und(a2, 1)[0]
			#a2_surr,_ = bct.null_model_und_sign(a2,bin_swaps=0)
		
		surrogate_similarity = similarity_metric(a1_surr,a2_surr)
		if surrogate_similarity > true_similarity:
			count+=1
		print 'surrogate similarity %.3f, true similarity %.3f'%(
			surrogate_similarity, true_similarity)
		print 'trial %i, p-value estimate so far %.4f'%(shuff, count/shuff)

	p = count/nshuff
	print 'test complete, p-value %.4f'%p
	return p 
