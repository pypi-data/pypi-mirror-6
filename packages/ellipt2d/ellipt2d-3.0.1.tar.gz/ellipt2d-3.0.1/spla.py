#!/usr/bin/env python

"""
Fast Linear Algebra functions
"""

import vector, sparse, dspla, math
import cvector, csparse
import csuperlu

def CGsolve(amat, x0, b, tol=1.0e-10, nmax = 1000, verbose=1):
    """
    Solve amat*x = b and return x using the conjugate gradient method
    """
    if amat.size()[0] != len(b) or amat.size()[1] != len(b):
            print('**Incompatible sizes in solve')
            print('**size()=', amat.size()[0], amat.size()[1])
            print('**len=', len(b))
    else:
            aij = dspla.toVIJ(amat)
            
            kvec = sparse.diag(amat) # preconditionner
            n = len(b)
            x = vector.vector(x0) # initial guess (make copy)
            r =  b - sparse.dot(amat, x)
            try:
                    w = r/kvec
            except: print('***singular kvec')
            p = vector.zeros(n);
            beta = 0.0;
            rho = dspla.YDotX(r, w);
            err = vector.norm(sparse.dot(amat,x) - b);
            k = 0
            if verbose: print(" conjugate gradient convergence (log error)")
            ncheck = max(1,nmax/40) # probe error up to 20 times
            while abs(err) > tol and k < nmax:

                    #p = w + beta*p;
                    dspla.TimesCPlusY(p, beta, w)

                    #z = sparse.dot(amat, p)
                    z = dspla.ADotX(aij,p)
                    
                    #alpha = rho/vector.dot(p,z)
                    alpha = rho/dspla.YDotX(p, z)
                    
                    #r = r - alpha*z
                    dspla.PlusCTimesY(r, -alpha, z)
                    
                    #w = r/kvec
                    w = dspla.XDivideY(r,kvec)
                    
                    rhoold = rho

                    #rho = vector.dot(r,w)
                    rho = dspla.YDotX(r, w)

                    #x = x + alpha*p
                    dspla.PlusCTimesY(x, alpha, p)
                    
                    beta = rho/rhoold

                    if (k/ncheck)*ncheck==k:
                        # computing err is costly, so only probe error
                        # every ncheck times
                        
                        #err = vector.norm(sparse.dot(amat, x) - b)
                        x2 = dspla.ADotX(aij,x)
                        dspla.PlusCTimesY(x2,-1.0,b)
                        err = math.sqrt(dspla.YDotX(x2,x2))
                        del x2
                        if verbose: print(k,' %5.1f ' % math.log10(err))
                        
                    k += 1
                    
            return vector.vector(x)


def starCGsolve(amat, x0, b, tol=1.0e-10, nmax = 1000, verbose=1):
    """
    Solve amat*x = b and return x using the conjugate gradient method
    """
    if amat.size()[0] != len(b) or amat.size()[1] != len(b):
            print('**Incompatible sizes in solve')
            print('**size()=', amat.size()[0], amat.size()[1])
            print('**len=', len(b))
    else:
            aij = dspla.toVIJ(amat)
            
            kvec = csparse.diag(amat) # preconditionner
            n = len(b)
            x = cvector.cvector(x0) # initial guess (make copy)
            #r =  b - csparse.dot(amat, x)
            r = cvector.cvector(b) # clone
            dspla.PlusCTimesY(r, -1., dspla.ADotX(aij,x))
            w = dspla.XDivideY(r, kvec)
##            try:
##                    w = r/kvec
##            except: print '***singular kvec'
            p = cvector.zeros(n);
            beta = 0.0;
            rho = dspla.YStarDotX(r, w);
            err = cvector.norm(csparse.dot(amat,x) - b);
            k = 0
            if verbose: print(" conjugate gradient convergence (log error)")
            ncheck = max(1,nmax/40) # probe error up to 20 times
            while abs(err) > tol and k < nmax:

                    #p = w + beta*p;
                    dspla.TimesCPlusY(p, beta, w)

                    #z = sparse.dot(amat, p)
                    z = dspla.ADotX(aij,p)
                    
                    #alpha = rho/vector.dot(p,z)
                    alpha = rho/dspla.YStarDotX(p, z)
                    
                    #r = r - alpha*z
                    dspla.PlusCTimesY(r, -alpha, z)
                    
                    #w = r/kvec
                    w = dspla.XDivideY(r,kvec)
                    
                    rhoold = rho

                    #rho = vector.dot(r,w)
                    rho = dspla.YStarDotX(r, w)

                    #x = x + alpha*p
                    dspla.PlusCTimesY(x, alpha, p)
                    
                    beta = rho/rhoold

                    if (k/ncheck)*ncheck==k:
                        # computing err is costly, so only probe error
                        # every ncheck times
                        
                        #err = vector.norm(sparse.dot(amat, x) - b)
                        x2 = dspla.ADotX(aij,x)
                        dspla.PlusCTimesY(x2,-1.0,b)
                        err = math.sqrt(abs(dspla.YStarDotX(x2,x2)))
                        del x2
                        if verbose: print(k,' %5.1f ' % math.log10(err))
                        
                    k += 1
                    
            return cvector.cvector(x)


def biCGsolve(amat, x0, b, tol=1.0e-10, nmax = 1000):
        # solve amat*x = b and return x using the bi-conjugate gradient method
        if amat.size()[0] != len(b) or amat.size()[1] != len(b):
                print('**Incompatible sizes in solve')
                print('**size()=', amat.size()[0], amat.size()[1])
                print('**len=', len(b))
        else:
                aij = dspla.toVIJ(amat)
                kvec = csparse.diag(amat) # preconditionner 
                n = len(b)
                x = cvector.cvector(x0) # initial guess, clone
                #r =  b - csparse.dot(amat, x)
                r = cvector.cvector(b) # clone
                dspla.PlusCTimesY(r, -1.0, dspla.ADotX(aij,x))
                rbar =  cvector.cvector(r) # copy
                
                #w = r/kvec
                w = dspla.XDivideY(r, kvec)
                #wbar = rbar/kvec
                wbar = dspla.XDivideY(rbar, kvec)
                
                p = cvector.zeros(n);
                pbar = cvector.zeros(n);
                beta = 0.0;

                #rho = cvector.dot(rbar, w);
                rho = dspla.YStarDotX(rbar, w)
                
                #err = cvector.norm(csparse.dot(amat,x) - b);
                x2 = dspla.ADotX(aij, x)
                dspla.PlusCTimesY(x2, -1.0, b)
                err = math.sqrt(abs(dspla.YStarDotX(x2,x2)))
                del x2
                
                k = 0
                print(" bi-conjugate gradient convergence (log error)")
                ncheck = max(1,nmax/40) # probe error up to 20 times
                while abs(err) > tol and k < nmax:
                    
                        #p = w + beta*p
                        dspla.TimesCPlusY(p, beta, w)
                        
                        #pbar = wbar + beta*pbar
                        dspla.TimesCPlusY(pbar, beta, wbar)
                        
                        #z = csparse.dot(amat, p)
                        z = cvector.cvector(dspla.ADotX(aij, p))
                        
                        #alpha = rho/cvector.dot(pbar, z)
                        alpha = rho/dspla.YStarDotX(pbar, z)
                        
                        #r = r - alpha*z
                        dspla.PlusCTimesY(r, -alpha, z)
                        
                        #rbar = rbar - alpha* csparse.dot(pbar, amat)
                        dspla.PlusCTimesY(rbar, -alpha, dspla.XStarDotA(pbar, aij))
                        
                        #w = r/kvec; wbar = rbar/kvec
                        w = cvector.cvector(dspla.XDivideY(r, kvec))
                        wbar = cvector.cvector(dspla.XDivideY(rbar, kvec))
                        
                        rhoold = rho
                        
                        #rho = cvector.dot(rbar, w)
                        rho = dspla.YStarDotX(rbar, w)
                        
                        #x = x + alpha*p
                        dspla.PlusCTimesY(x, alpha, p)
                        
                        beta = rho/rhoold

                        if (k/ncheck)*ncheck==k:
                            # computing err is costly, so only probe error
                            # every ncheck times

                            #err = cvector.norm(csparse.dot(amat, x) - b);
                            x2 = dspla.ADotX(aij, x)
                            dspla.PlusCTimesY(x2, -1.0, b)
                            err = math.sqrt(abs(dspla.YStarDotX(x2,x2)))
                            del x2

                            try:
                                    print(k,' %5.1f ' % math.log10(abs(err)))
                            except: print(k, abs(err))
                            
                        k += 1
                        
                return cvector.cvector(x)

def eigen(amat, bmat, lambd0, v0, tol=1.e-10, nmax=1000, verbose=0):
	"""
	solve eigenproblem amat*v = lambd bmat*v
	tol: max tolerance |amat*v - lambd bmat*v|
	nmax: max no of iterations
	"""

	try:
		import csparse, cvector
	except:
		print('Cannot import csparse or cvector')

	if amat.size()[0] != bmat.size()[0] or \
	   amat.size()[1] != bmat.size()[1] or \
	   len(v0) != amat.size()[1]:
		print('incompatible sizes in eigen')
		print(amat.size()[0], bmat.size()[0])
		print(amat.size()[1], bmat.size()[1], len(v0))
		return None

	lambd = lambd0
	v     = cvector.cvector(v0)
        
        bij = dspla.toVIJ(bmat)
	for i in range(nmax):
		cmat = amat - lambd*bmat
                cij = dspla.toVIJ(cmat)
                
		#residue = abs(cvector.norm(csparse.dot(cmat, v)))
                x2 = dspla.ADotX(cij, v)
                residue = math.sqrt(abs(dspla.YDotX(x2,x2)))

		print('-'*20)
		try:
			print('iteration %d lambd=(%f,%f) residue=%10.2e' % \
			      (i, lambd.real, lambd.imag, residue))
		except:
			print('iteration %d lambd=(%f,0.) residue=%10.2e' % \
			      (i, lambd, residue))

		if residue < tol: break

		#rhs = csparse.dot(bmat,v)
                rhs = dspla.ADotX(bij, v)

                thistol = 1.e-6 #max(tol, 0.1**(2*i)) # decrease tol
		newv = csuperlu.solve(cmat, rhs)
##                newv = cvector.cvector(starCGsolve(csparse.csparse(cmat), x0=cvector.cvector(v), \
##                                   b=cvector.cvector(rhs), tol=thistol, nmax = 1000))

		#newv_b_v    = cvector.dot(newv, rhs)
                newv_b_v = dspla.YStarDotX(newv, rhs)
                
		#newv_b_newv = cvector.dot(newv, csparse.dot(bmat, newv))
                newv_b_newv = dspla.YStarDotX(newv, dspla.ADotX(bij, newv))
                
		lambd += newv_b_v/newv_b_newv
		#v = cvector.cvector( newv/cvector.norm(newv) )
                v = cvector.cvector( newv/math.sqrt(abs(dspla.YStarDotX(newv, newv)) ) )

	return [lambd, v, residue, i]
