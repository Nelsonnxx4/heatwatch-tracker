async def test_health_is_public(anon_client):
    response = await anon_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_missing_api_key_rejected(anon_client):
    response = await anon_client.get("/cities")
    assert response.status_code == 401


async def test_wrong_api_key_rejected(anon_client):
    response = await anon_client.get("/cities", headers={"X-API-Key": "nope"})
    assert response.status_code == 401


async def test_list_cities_sorted_by_name(client, seeded):
    response = await client.get("/cities")
    assert response.status_code == 200
    assert [c["slug"] for c in response.json()] == ["lagos", "makurdi"]


async def test_temperature_range_filter(client, seeded):
    response = await client.get(
        "/cities/makurdi/temperature",
        params={"from": "2026-11-18T00:00:00", "to": "2026-11-18T05:00:00"},
    )
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 6
    assert rows[0]["heat_index_c"] > rows[0]["temperature_c"]
    assert rows[0]["observed_at"] < rows[-1]["observed_at"]


async def test_temperature_limit_returns_latest_oldest_first(client, seeded):
    response = await client.get("/cities/abuja/temperature", params={"limit": 5})
    rows = response.json()
    assert len(rows) == 5
    assert rows[-1]["observed_at"].startswith("2026-11-20T23:00")


async def test_unknown_city_is_404(client, seeded):
    response = await client.get("/cities/atlantis/temperature")
    assert response.status_code == 404


async def test_inverted_range_is_422(client, seeded):
    response = await client.get(
        "/cities/abuja/temperature",
        params={"from": "2026-11-19T00:00:00", "to": "2026-11-18T00:00:00"},
    )
    assert response.status_code == 422


async def test_heat_summary(client, seeded):
    response = await client.get("/cities/abuja/heat-summary", params={"days": 7})
    assert response.status_code == 200
    body = response.json()
    assert body["city"]["slug"] == "abuja"
    assert len(body["days"]) == 3
    assert body["anomaly_c"] is None  # fewer than 7 baseline days
    assert body["current"]["heat_category"] in {"extreme_caution", "danger", "extreme_danger"}


async def test_rankings_put_hottest_city_first(client, seeded):
    response = await client.get("/rankings/hottest")
    assert response.status_code == 200
    ranking = response.json()
    assert [r["city"]["slug"] for r in ranking] == ["makurdi", "lagos"]
    assert ranking[0]["heat_index_max_c"] > ranking[1]["heat_index_max_c"]


async def test_rankings_empty_database(client):
    response = await client.get("/rankings/hottest")
    assert response.status_code == 200
    assert response.json() == []
