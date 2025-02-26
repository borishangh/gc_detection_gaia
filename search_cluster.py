import os
import numpy as np
import pandas as pd
from astroquery.gaia import Gaia
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

# Directory to save results and figures
results_file = "clusters_found.csv"
progress_file = "scanning_progress.txt"
figures_dir = "cluster_figures"

# Create the directory for figures if it doesn't exist
os.makedirs(figures_dir, exist_ok=True)

def get_gaia_data_patch(ra, dec, radius_deg=10):
    """
    Fetch Gaia data for a circular region around given RA/Dec (2'x2').
    
    Parameters:
    ra (float): Right Ascension of the target (in degrees).
    dec (float): Declination of the target (in degrees).
    radius_deg (float): Radius of the search region in degrees (default is ~2 arcminutes).
    
    Returns:
    data (pandas DataFrame): Gaia data for the specified region.
    """
    query = f"""
    SELECT 
        source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag, bp_rp
    FROM gaiadr3.gaia_source
    WHERE 1=CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', {ra}, {dec}, {radius_deg})
    )
    AND parallax > 0
    AND pmra IS NOT NULL
    AND pmdec IS NOT NULL
    AND phot_g_mean_mag IS NOT NULL
    AND bp_rp IS NOT NULL
    """
    
    job = Gaia.launch_job(query)
    results = job.get_results().to_pandas()
    return results

def save_cluster(ra, dec, probability, labels, data):
    """
    Save the detected cluster's information and plot the figures.
    
    Parameters:
    ra (float): Right Ascension of the patch.
    dec (float): Declination of the patch.
    probability (float): Cluster probability score.
    labels (array): Cluster labels from DBSCAN.
    data (DataFrame): Gaia data for the patch.
    """
    # Append cluster info to the results file
    with open(results_file, 'a') as f:
        f.write(f"{ra},{dec},{probability}\n")
    
    # Plot and save the figures
    fig, ax = plt.subplots(figsize=(8,6))
    scatter = ax.scatter(data['pmra'], data['pmdec'], c=labels, cmap='plasma', s=1, alpha=0.5)
    plt.xlabel('Proper Motion in RA (mas/yr)')
    plt.ylabel('Proper Motion in Dec (mas/yr)')
    plt.title(f'Clusters at RA: {ra}, Dec: {dec}')
    plt.colorbar(scatter)
    
    
    ax_inset = plt.axes([0.18, 0.6, 0.25, 0.25])
    ax_inset.scatter(data['bp_rp'], data['phot_g_mean_mag'], c=labels, cmap='plasma', s=1, alpha=0.5)
    ax_inset.invert_yaxis()
    ax_inset.set_xlabel('BP - RP Color')
    ax_inset.set_ylabel('G-band Magnitude')
    ax_inset.set_title('Clustered CMD')
    
    # change the fontsize of the inset plot
    for item in ([ax_inset.title, ax_inset.xaxis.label, ax_inset.yaxis.label] +
                    ax_inset.get_xticklabels() + ax_inset.get_yticklabels()):
        item.set_fontsize(5)
    
    plt.savefig(f"{figures_dir}/cluster_RA{ra}_DEC{dec}.png")
    plt.close()

def scan_sky_and_find_clusters(ra_range, dec_range, patch_size_arcmin=10*60):
    """
    Scan the sky in given RA/Dec range, patch by patch, and apply clustering to find globular clusters.
    Resume scanning from the last processed patch if interrupted.
    
    Parameters:
    ra_range (tuple): Range of Right Ascension to scan (in degrees).
    dec_range (tuple): Range of Declination to scan (in degrees).
    patch_size_arcmin (float): Size of the patch to scan (default is 20 arcminutes).
    """
    patch_size_deg = patch_size_arcmin / 60  # Convert arcminutes to degrees

    # Load or create progress file
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            scanned_patches = set(f.read().splitlines())
    else:
        scanned_patches = set()

    ra_min, ra_max = ra_range
    dec_min, dec_max = dec_range
    
    ra_steps = np.arange(ra_min, ra_max, patch_size_deg)
    dec_steps = np.arange(dec_min, dec_max, patch_size_deg)
    
    for ra in ra_steps:
        for dec in dec_steps:
            patch_id = f"{ra:.4f}_{dec:.4f}"
            if patch_id in scanned_patches:
                continue  # Skip already scanned patches

            # Get Gaia data for the current patch
            data = get_gaia_data_patch(ra, dec, patch_size_deg / 2)
            
            if len(data) < 10:
                continue  # Skip if too few stars in the patch

            # Apply DBSCAN clustering on proper motion and parallax
            features = data[['pmra', 'pmdec', 'parallax']].values
            db = DBSCAN(eps=0.5, min_samples=5).fit(features)
            labels = db.labels_
            
            # Compute "cluster probability" as the ratio of stars in clusters to total stars
            num_clustered_stars = np.sum(labels != -1)
            total_stars = len(labels)
            cluster_probability = num_clustered_stars / total_stars
            
            # Save the results if there are clustered stars
            if num_clustered_stars > 0:
                save_cluster(ra, dec, cluster_probability, labels, data)

            # Log the scanned patch
            with open(progress_file, 'a') as f:
                f.write(f"{patch_id}\n")

# Define the RA/Dec range for scanning (full sky for global scan)
ra_range = (0, 360)  # Full RA range in degrees
dec_range = (-90, 90)  # Full Declination range in degrees

# ra_range = (0, 1)  # Full RA range in degrees
# dec_range = (0, 1)  # Full Declination range in degrees


# Perform sky scan and find clusters
scan_sky_and_find_clusters(ra_range, dec_range)
