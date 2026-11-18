from concurrent.futures import ThreadPoolExecutor

from support import FARM_DEMO, plot_payload

NASTY = "Block A:1 100%?"


def test_names_with_sql_looking_characters_round_trip(client):
    farm = client.post("/v1/farms", json={"name": NASTY}).json()
    plot = client.post("/v1/plots", json=plot_payload(farm_id=farm["id"], name=NASTY)).json()

    assert client.get(f"/v1/farms/{farm['id']}").json()["name"] == NASTY
    assert client.get(f"/v1/plots/{plot['id']}").json()["name"] == NASTY


def test_next_write_works_after_a_conflict(client):
    assert client.post("/v1/plots", json=plot_payload(name="Same")).status_code == 201
    assert client.post("/v1/plots", json=plot_payload(name="Same")).status_code == 409

    assert client.post("/v1/plots", json=plot_payload(name="Different")).status_code == 201


def test_concurrent_creates_with_same_name_give_one_201_and_one_409(client):
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda _: client.post("/v1/plots", json=plot_payload(name="Race")).status_code,
                range(2),
            )
        )

    assert sorted(results) == [201, 409]
