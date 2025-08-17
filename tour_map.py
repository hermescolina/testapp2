"""Utility to display tour price map for given location."""

from __future__ import annotations


def display_tour_price_map(location: str) -> 'folium.Map':
    """Display an interactive map with the tour price shown at the location.

    Parameters
    ----------
    location: str
        Human readable location, e.g. "El Nido, Palawan".

    Returns
    -------
    folium.Map
        Map object with price label at the location.

    Notes
    -----
    Database connection details are read from the environment variables
    ``DB_HOST``, ``DB_USER``, ``DB_PASSWORD`` and ``DB_NAME`` with sensible
    defaults for local development.  The function will raise ``ValueError``
    if the location cannot be geocoded or no price is found in the database.
    """

    import os
    import requests
    import folium
    import mysql.connector
    from mysql.connector import Error as MySQLError

    if not location:
        raise ValueError("location must not be empty")

    # 1. Geocode the location using OpenStreetMap Nominatim
    geocode_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1}
    headers = {"User-Agent": "tour-price-map/1.0"}

    try:
        response = requests.get(geocode_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()
    except requests.RequestException as exc:
        raise ValueError(f"Error requesting geocode data: {exc}") from exc

    if not results:
        raise ValueError(f"Location '{location}' not found")

    lat = float(results[0]["lat"])
    lon = float(results[0]["lon"])

    # 2. Query the database for the tour price
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "tour_db"),
        )
        cursor = conn.cursor()
        query = (
            "SELECT i.price FROM items i "
            "JOIN tours t ON t.item_id = i.id "
            "WHERE t.location = %s LIMIT 1"
        )
        cursor.execute(query, (location,))
        row = cursor.fetchone()
    except MySQLError as exc:
        raise ValueError(f"Database error: {exc}") from exc
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    if not row:
        raise ValueError(f"Price for location '{location}' not found in database")

    price = row[0]

    # 3. Create the map with price label using DivIcon
    tour_map = folium.Map(location=[lat, lon], zoom_start=13)
    icon_html = (
        f'<div style="font-size: 14px; font-weight: bold; color: black">{price} PHP</div>'
    )
    folium.Marker(
        location=[lat, lon],
        icon=folium.DivIcon(html=icon_html)
    ).add_to(tour_map)

    # 4. Attempt to display map if running in an interactive environment
    try:
        from IPython.display import display

        display(tour_map)
    except Exception:
        # Ignore environments where display is unavailable
        pass

    return tour_map
