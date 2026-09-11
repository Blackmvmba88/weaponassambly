from __future__ import annotations

from weaponassambly.scene import validate_scene_manifest


def valid_manifest():
    transform = {
        "location": [0.0, 0.0, 0.0],
        "rotation_euler": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
    }
    return {
        "scene_schema_version": 1,
        "platform": "BM-S7",
        "root": "BM_SIDEARM_ROOT",
        "collections": [
            "00_ROOT",
            "10_CORE",
            "20_TOP",
            "30_FRONT",
            "40_BOTTOM",
            "50_MAG",
            "60_COSMETICS",
            "70_SOCKETS",
            "80_RIG",
            "90_GUIDES",
        ],
        "sockets": {
            "SOCKET_TOP": dict(transform),
            "SOCKET_BOTTOM": dict(transform),
            "SOCKET_FRONT": dict(transform),
            "SOCKET_MAG": dict(transform),
            "SOCKET_GRIP": dict(transform),
        },
    }


def test_scene_manifest_accepts_canonical_contract():
    result = validate_scene_manifest(valid_manifest())
    assert result.ok
    assert result.errors == ()


def test_scene_manifest_rejects_missing_socket():
    payload = valid_manifest()
    del payload["sockets"]["SOCKET_TOP"]

    result = validate_scene_manifest(payload)
    assert not result.ok
    assert "missing socket: SOCKET_TOP" in result.errors


def test_scene_manifest_reports_missing_sockets_in_stable_order():
    payload = valid_manifest()
    for socket_name in ("SOCKET_TOP", "SOCKET_BOTTOM", "SOCKET_GRIP"):
        del payload["sockets"][socket_name]

    result = validate_scene_manifest(payload)
    missing_errors = [error for error in result.errors if error.startswith("missing socket:")]

    assert missing_errors == [
        "missing socket: SOCKET_BOTTOM",
        "missing socket: SOCKET_GRIP",
        "missing socket: SOCKET_TOP",
    ]


def test_scene_manifest_rejects_non_unit_socket_scale():
    payload = valid_manifest()
    payload["sockets"]["SOCKET_MAG"]["scale"] = [1.0, 2.0, 1.0]

    result = validate_scene_manifest(payload)
    assert not result.ok
    assert "socket SOCKET_MAG scale must be 1,1,1" in result.errors


def test_scene_manifest_rejects_unknown_socket():
    payload = valid_manifest()
    payload["sockets"]["SOCKET_UNKNOWN"] = {
        "location": [0.0, 0.0, 0.0],
        "rotation_euler": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
    }

    result = validate_scene_manifest(payload)
    assert not result.ok
    assert "unknown socket: SOCKET_UNKNOWN" in result.errors


def test_scene_manifest_preserves_numeric_subclass_compatibility():
    class SceneInt(int):
        pass

    payload = valid_manifest()
    payload["sockets"]["SOCKET_TOP"]["location"] = [SceneInt(0), SceneInt(0), SceneInt(0)]

    result = validate_scene_manifest(payload)
    assert result.ok
    assert result.errors == ()


def test_scene_manifest_preserves_invalid_scale_diagnostics():
    payload = valid_manifest()
    payload["sockets"]["SOCKET_MAG"]["scale"] = [1.0, "bad", 1.0]

    result = validate_scene_manifest(payload)
    assert not result.ok
    assert "socket SOCKET_MAG.scale must contain only numbers" in result.errors
    assert "socket SOCKET_MAG scale must be 1,1,1" in result.errors


def test_scene_manifest_rejects_bool_vector_component():
    payload = valid_manifest()
    payload["sockets"]["SOCKET_GRIP"]["location"] = [0.0, True, 0.0]

    result = validate_scene_manifest(payload)
    assert not result.ok
    assert "socket SOCKET_GRIP.location must contain only numbers" in result.errors


def test_scene_manifest_preserves_scale_subclass_float_coercion():
    class SceneInt(int):
        def __sub__(self, other):
            raise AssertionError("scale validation must coerce numeric subclasses with float()")

    payload = valid_manifest()
    payload["sockets"]["SOCKET_TOP"]["scale"] = [SceneInt(1), SceneInt(1), SceneInt(1)]

    result = validate_scene_manifest(payload)
    assert result.ok
    assert result.errors == ()
