# utils for working with 3d-protein structures
import numpy as np 
import torch


def shape_and_backend(x,y,backend):
    """ pack here for reuse. 
        turns input into (B x D x N) and chooses backend
    """
    # auto type infer mode
    if backend == "auto":
        backend = "torch" if isinstance(A, torch.tensor) else "numpy"
    # check shapes
    if len(x.shape) == len(y.shape):
        while len(A.shape) < 3:
            if backend == "torch":
                x = x.unsqueeze(dim=0)
                y = y.unsqueeze(dim=0)
            else:
                x = np.expand_dims(x, axis=0)
                y = np.expand_dims(y, axis=0)
    else:
        raise ValueError("Shapes of A and B must match.")

    return x,y,backend


# alignment

def kabsch_torch(X, Y):
    """ Kabsch alignment of X with Y as reference. 
        Assumes x,y are both (B x D x N). See below for wrapper.
    """
    raise NotImplementedError("Torch backend not yet implemented")
    return X_, Y_

def kabsch_numpy(X, Y):
    """ Kabsch alignment of X with Y as reference. 
        Assumes x,y are both (B x D x N). See below for wrapper.
    """

    return X_, Y_


# metrics - more formulas here: http://predictioncenter.org/casp12/doc/help.html

def rmsd_torch(X, Y):
    """ Assumes x,y are both (B x D x N). See below for wrapper. """
    return torch.sqrt( torch.mean((X - Y)**2, axis=(-1, -2)) )

def rmsd_numpy(X, Y):
    """ Assumes x,y are both (B x D x N). See below for wrapper. """
    return np.sqrt( np.mean((X - Y)**2, axis=(-1, -2)) )

def gdt_torch(X, Y, cutoffs, weights=None):
    """ Assumes x,y are both (B x D x N). see below for wrapper.
        * cutoffs is a list of `K` thresholds
        * weights is a list of `K` weights (1 x each threshold)
    """
    if weights is None:
        weights = torch.ones(1,len(weights))
    else:
        weights = torch.tensor([weights]).to(x.device)
    # set zeros and fill with values
    GDT = torch.zeros(X.shape[0], len(cutoffs), device=X.device) 
    dist = ((X - Y)**2).sum(dim=1).sqrt()
    # iterate over thresholds
    for i,cutoff in enumerate(cutoffs):
        GDT[:, i] = (dist <= cutoff).float().sum(dim=-1)
    # weighted mean
    return (GDT*weights).mean(-1)

def gdt_numpy(X, Y, cutoffs, weights=None):
    """ Assumes x,y are both (B x D x N). see below for wrapper.
        * cutoffs is a list of `K` thresholds
        * weights is a list of `K` weights (1 x each threshold)
    """
    if weights is None
        weights = np.ones( (1,len(weights)) )
    else:
        weights = np.array([weights])
    # set zeros and fill with values
    GDT = torch.zeros( (X.shape[0], len(cutoffs)) )
    dist = ((X - Y)**2).sum(axis=1).sqrt()
    # iterate over thresholds
    for i,cutoff in enumerate(cutoffs):
        GDT[:, i] = (dist <= cutoff).float().sum(axis=-1)
    # weighted mean
    return (GDT*weights).mean(-1)

def tmscore_torch(X, Y):
    """ Assumes x,y are both (B x D x N). see below for wrapper. """
    L = X.shape[-1]
    d0 = 1.24 * np.cbrt(L - 15) - 1.8
    # get distance
    dist = ((X - Y)**2).sum(dim=1).sqrt()
    # formula (see wrapper for source): 
    return (1 / (1 + (dist/d0)**2)).mean(dim=-1)

def tmscore_numpy(X, Y):
    """ Assumes x,y are both (B x D x N). see below for wrapper. """
    L = X.shape[-1]
    d0 = 1.24 * np.cbrt(L - 15) - 1.8
    # get distance
    dist = np.sqrt( ((X - Y)**2).sum(axis=1) )
    # formula (see wrapper for source): 
    return (1 / (1 + (dist/d0)**2)).mean(axis=-1)

################
### WRAPPERS ###
################

def RMSD(A, B, backend="auto"):
    """ Returns RMSD score as defined here (lower is better):
        https://en.wikipedia.org/wiki/
        Root-mean-square_deviation_of_atomic_positions
        * Inputs: 
            * A,B are (B x 3 x N) or (3 x N)
            * backend: one of ["numpy", "torch", "auto"] for backend choice
        * Outputs: tensor/array of size (B,)
    """
    A, B, backend = shape_and_backend(A, B, backend)
    # run calcs
    if backend == "torch":
        return rmsd_torch(A, B)
    else:
        return rmsd_numpy(A, B)


def GDT(A,B, mode="TS", cutoffs=[1,2,4,8], weights=None, backend="auto"):
    """ Returns GDT score as defined here (highre is better):
        Supports both TS and HA
        http://predictioncenter.org/casp12/doc/help.html
        * Inputs:
            * A,B are (B x 3 x N) (np.array or torch.tensor)
            * cutoffs: defines thresholds for gdt
            * weights: list containing the weights
            * mode: one of ["numpy", "torch", "auto"] for backend
        * Outputs: tensor/array of size (B,)
    """
    A, B, backend = shape_and_backend(A, B, backend)
    # define cutoffs for each type of gdt and weights
    cutoffs = [0.5,1,2,4] if func == "HA" else [1,2,4,8]
    # calculate GDT
    if mode == "torch":
        return gdt_torch(A, B, cutoffs, weights=weights)
    else:
        return gdt_numpy(A, B, cutoffs, weights=weights)


def TMscore(A,B,backend="auto"):
    """ Returns TMscore as defined here (higher is better):
        >0.5 (likely) >0.6 (highly likely) same folding. 
        = 0.2. https://en.wikipedia.org/wiki/Template_modeling_score
        Warning! It's not exactly the code in:
        https://zhanglab.ccmb.med.umich.edu/TM-score/TMscore.cpp
        but will suffice for now. 
        Inputs: 
            * A,B are (B x 3 x N) (np.array or torch.tensor)
            * mode: one of ["numpy", "torch", "auto"] for backend
        Outputs: tensor/array of size (B,)
    """
    A, B, backend = shape_and_backend(A, B, backend)
    # run calcs
    if backend == "torch":
        return tmscore_torch(A, B)
    else:
        return tmscore_numpy(A, B)


