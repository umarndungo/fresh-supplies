"""Geospatial dynamic route optimization using NetworkX.

Implements a spoilage-aware friction score so that routes minimise
transport time, thermal spoilage exposure, and handling cost while
prioritising destinations with higher expected revenue.
"""

import networkx as nx
import numpy as np
import pandas as pd


def build_friction_score(
    distance_km: float,
    transit_hours: float,
    spoilage_risk: float,
    temp_c: float = 25.0,
    weight_time: float = 0.35,
    weight_spoilage: float = 0.45,
    weight_cost: float = 0.20,
) -> float:
    """Composite edge weight: time + spoilage + cost, all normalised.

    Lower friction = more desirable route. Spoilage risk is the dominant
    term by default, since it directly impacts revenue retention.
    """
    time_norm = transit_hours / 24.0
    spoilage_norm = spoilage_risk / 100.0
    heat_factor = max(0.0, (temp_c - 30.0)) / 10.0  # extra penalty when >30C
    cost_factor = distance_km / 500.0
    return (
        weight_time * time_norm
        + weight_spoilage * (spoilage_norm + heat_factor)
        + weight_cost * cost_factor
    )


def estimate_revenue_retained(quantity_kg, unit_price, spoilage_pct):
    """Revenue kept after subtracting spoilage loss."""
    return quantity_kg * unit_price * (1.0 - spoilage_pct / 100.0)


def calculate_optimal_route(
    graph_data: dict,
    start_node: str,
    end_node: str,
    spoilage_risk_map: dict | None = None,
) -> list:
    """Computes lowest-spoilage/shortest transit path to market destinations."""
    G = nx.Graph()
    for edge in graph_data.get("edges", []):
        from_node = edge["from"]
        to_node = edge["to"]
        distance = edge.get("distance_km", 1.0)
        hours = edge.get("transit_hours", 1.0)
        temp = edge.get("temp_c", 25.0)
        risk = edge.get("spoilage_risk", 1.0)
        if spoilage_risk_map:
            base_risk = spoilage_risk_map.get(from_node, 1.0)
            risk = base_risk + edge.get("spoilage_risk", 0.0)
        friction = build_friction_score(distance, hours, risk, temp)
        G.add_edge(from_node, to_node, weight=friction)

    try:
        path = nx.shortest_path(G, source=start_node, target=end_node, weight="weight")
        return path
    except nx.NetworkXNoPath:
        return []


def recommend_market_destinations(
    graph_data: dict,
    start_node: str,
    crops_lookup: dict | None = None,
    prices_lookup: dict | None = None,
    spoilage_risk_map: dict | None = None,
    top_n: int = 3,
) -> list:
    """Ranks destination markets by expected revenue retention.

    For each market reachable from start_node, computes the best
    (lowest-friction) path and combines distance/spoilage with
    price to recommend the most profitable destinations.
    """
    G = nx.Graph()
    for edge in graph_data.get("edges", []):
        from_node = edge["from"]
        to_node = edge["to"]
        distance = edge.get("distance_km", 1.0)
        hours = edge.get("transit_hours", 1.0)
        temp = edge.get("temp_c", 25.0)
        risk = edge.get("spoilage_risk", 1.0)
        if spoilage_risk_map:
            risk = spoilage_risk_map.get(from_node, 1.0) + edge.get("spoilage_risk", 0.0)
        friction = build_friction_score(distance, hours, risk, temp)
        G.add_edge(from_node, to_node, weight=friction)

    markets = [n for n in G.nodes if n != start_node]
    rankings = []
    for market in markets:
        try:
            path = nx.shortest_path(G, source=start_node, target=market, weight="weight")
        except nx.NetworkXNoPath:
            continue

        # Estimate the spoilage % of the chosen path
        spoilage = sum(
            edge.get("spoilage_risk", 1.0)
            for edge in _edges_along_path(G, path)
        )
        transit_hours = sum(
            edge.get("transit_hours", 1.0)
            for edge in _edges_along_path(G, path)
        )

        price = 1.0
        if prices_lookup:
            price = prices_lookup.get(market) or prices_lookup.get(market.upper(), 1.0)
        revenue_retained = estimate_revenue_retained(
            quantity_kg=100.0, unit_price=price, spoilage_pct=min(spoilage, 99.0)
        )
        rankings.append(
            {
                "market": market,
                "path": path,
                "transit_hours": round(transit_hours, 2),
                "spoilage_pct": round(min(spoilage, 99.0), 2),
                "price_per_kg": price,
                "revenue_retained_per_100kg": round(revenue_retained, 2),
            }
        )

    rankings.sort(key=lambda r: r["revenue_retained_per_100kg"], reverse=True)
    return rankings[:top_n]


def _edges_along_path(G, path):
    edges = []
    for i in range(len(path) - 1):
        edges.append(G.get_edge_data(path[i], path[i + 1]))
    return [e for e in edges if e is not None]


def _haversine_km(lat1, lon1, lat2, lon2):
    import math
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def recommend_market_for_shipment(
    shipment: dict,
    model_bundle: dict,
    market_prices: pd.DataFrame,
    top_n: int = 5,
) -> list:
    """Ranks markets for a single shipment by revenue retained.

    Couples the trained spoilage model with market pricing:
    for each destination the shipment could reach, it predicts the spoilage
    probability on that route (from thermal load + transit + distance) and
    scores revenue_retained = qty x price x (1 - spoilage_prob).

    shipment keys: crop_type, latitude, longitude, Temperature_C,
                   Shift (optional), baseline_loss_pct (optional),
                   quantity_kg (default 100)
    model_bundle: {"model": PredictiveModels, "feature_names": [...]} as saved
                  by train_food_model.
    """
    model = model_bundle["model"]
    feature_names = model_bundle["feature_names"]

    crop = shipment["crop_type"]
    quantity_kg = float(shipment.get("quantity_kg", 100.0))
    transit_hours = float(shipment.get("Transit_Duration_Hr", 4.0))
    temp_c = float(shipment.get("Temperature_C", 25.0))
    thermal = max(0.0, temp_c - 25.0) * transit_hours
    baseline_loss = float(shipment.get("baseline_loss_pct", 10.0))

    crop_prices = market_prices[market_prices["crop"] == crop].copy()
    feature_names = model.feature_names

    rankings = []
    for _, mkt in crop_prices.iterrows():
        distance_km = _haversine_km(
            shipment["latitude"], shipment["longitude"],
            mkt["market_lat"], mkt["market_lon"],
        )
        features = np.zeros(len(feature_names))
        feature_idx = {name: i for i, name in enumerate(feature_names)}
        for name, value in [
            ("Temperature_C", temp_c),
            ("Pressure_PSI", float(shipment.get("Pressure_PSI", 30.0))),
            ("Transit_Duration_Hr", transit_hours),
            ("baseline_loss_pct", baseline_loss),
            ("Thermal_Heat_Exposure", thermal),
            ("Distance_To_Market_Km", distance_km),
            ("price_per_kg", mkt["price_per_kg"]),
        ]:
            if name in feature_idx:
                features[feature_idx[name]] = value

        import pandas as _pd2
        spoilage_prob = float(model.predict_proba(_pd2.DataFrame([features], columns=feature_names))[0])
        revenue_retained = quantity_kg * mkt["price_per_kg"] * (1.0 - spoilage_prob)
        rankings.append(
            {
                "market_id": mkt["market_id"],
                "market_name": mkt["market_name"],
                "region": mkt["region"],
                "distance_km": round(distance_km, 1),
                "price_per_kg": mkt["price_per_kg"],
                "spoilage_prob": round(spoilage_prob, 3),
                "revenue_retained": round(revenue_retained, 2),
            }
        )

    rankings.sort(key=lambda r: r["revenue_retained"], reverse=True)
    return rankings[:top_n]