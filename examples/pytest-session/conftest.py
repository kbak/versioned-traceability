def pytest_collection_modifyitems(items):
    # Collection-time properties survive skip/xfail and setup failures.
    # Only the test artifact ID is repeated; requirement links stay in OFT.
    for item in items:
        for marker in item.iter_markers(name="oft_id"):
            for identifier in marker.args:
                item.user_properties.append(("oft_id", identifier))
