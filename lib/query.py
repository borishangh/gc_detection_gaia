from astroquery.gaia import Gaia
from astropy.table import Table


def write_query(
    ra, dec, shape, r, limit=10000, all_rows=False, order_by_dist=True
):
    if shape.upper() == "CIRCLE":
        where_clause = f"WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, {r}))=1"
    elif shape.upper() == "BOX":
        where_clause = f"WHERE CONTAINS(POINT('ICRS', ra, dec), BOX('ICRS', {ra}, {dec}, {r}, {r}))=1"
    else:
        raise ValueError("Invalid shape. Shape must be 'CIRCLE' or 'BOX'.")

    rows = "*" if all_rows else "source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag, bp_rp"

    query = f"""
    SELECT{f" TOP {limit}" if limit else  ""}
    {rows}, DISTANCE(POINT('ICRS', ra, dec), POINT('ICRS', {ra}, {dec})) AS dist
    FROM gaiadr3.gaia_source
    {where_clause}
    AND parallax > 0
    AND pmra IS NOT NULL
    AND pmdec IS NOT NULL
    AND phot_g_mean_mag IS NOT NULL
    AND bp_rp IS NOT NULL
    {"ORDER BY dist ASC" if order_by_dist else ""}
    """

    return query


def query_to_df(query):
    try:
        job = Gaia.launch_job(query)
        result = job.get_results()
        df = Table.to_pandas(result)
        return df

    except Exception as e:
        print(f"Error executing query: {e}")
        return None