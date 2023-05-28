import mne


def get_inverse_operator(epochs, fwd, cov_params=None, inv_params=None):

    # Compute noise covariance
    if cov_params is None:
        tmax, method, rank = 0.0, ("shrunk", "empirical"), None
        noise_cov = mne.compute_covariance(epochs, tmax=tmax, method=method, rank=rank)
    else:
        noise_cov = mne.compute_covariance(epochs, tmax=cov_params["tmax"], method=cov_params["method"],
                                           rank=cov_params["rank"])

    if inv_params is None:
        inv = mne.minimum_norm.make_inverse_operator(info=epochs.info, forward=fwd, noise_cov=noise_cov,
                                                     loose=0.2, depth=0.8)
    else:
        inv = mne.minimum_norm.make_inverse_operator(info=epochs.info, forward=fwd, noise_cov=noise_cov,
                                                     loose=inv_params["loose"], depth=inv_params["depth"])

    return inv
