# Data audit report

Read-only audit of the three supplied source workbooks. Original files were not modified.

## fake: `fake_users training.xlsx`

- Rows: 1998
- Columns: 35
- Exact duplicate rows: 0
- Label distribution: `{'1': 1998}`
- Potential identifier columns found: `['id', 'screen_name', 'name', 'url', 'profile_image_url', 'profile_image_url_https', 'dataset']`

### Column types and missing values

| Column | Type | Missing | Unique non-missing |
|---|---:|---:|---:|
| `id` | float64 | 0 | 979 |
| `name` | str | 693 | 835 |
| `screen_name` | str | 730 | 834 |
| `statuses_count` | float64 | 0 | 940 |
| `followers_count` | float64 | 0 | 903 |
| `friends_count` | float64 | 0 | 984 |
| `favourites_count` | float64 | 0 | 18 |
| `listed_count` | float64 | 0 | 3 |
| `created_at` | str | 695 | 807 |
| `url` | int64 | 0 | 1 |
| `lang` | str | 713 | 1 |
| `time_zone` | str | 1995 | 2 |
| `location` | str | 757 | 683 |
| `default_profile` | float64 | 0 | 955 |
| `default_profile_image` | float64 | 0 | 5 |
| `geo_enabled` | float64 | 0 | 2 |
| `profile_image_url` | str | 714 | 846 |
| `profile_banner_url` | str | 1996 | 1 |
| `profile_use_background_image` | float64 | 0 | 972 |
| `profile_background_image_url_https` | str | 705 | 7 |
| `profile_text_color` | object | 716 | 3 |
| `profile_image_url_https` | str | 723 | 833 |
| `profile_sidebar_border_color` | str | 686 | 4 |
| `profile_background_tile` | float64 | 0 | 2 |
| `profile_sidebar_fill_color` | str | 698 | 3 |
| `profile_background_image_url` | str | 681 | 6 |
| `profile_background_color` | object | 713 | 4 |
| `profile_link_color` | object | 715 | 5 |
| `utc_offset` | float64 | 0 | 2 |
| `protected` | int64 | 0 | 1 |
| `verified` | int64 | 0 | 1 |
| `description` | str | 957 | 658 |
| `updated` | datetime64[us] | 711 | 1 |
| `dataset` | str | 691 | 1 |
| `is_fake` | int64 | 0 | 1 |

### Duplicate identifier diagnostics

| Column | Unique non-missing | Duplicate non-missing | Zero placeholders |
|---|---:|---:|---:|
| `id` | 978 | 0 | 1020 |
| `screen_name` | 834 | 434 | 0 |
| `name` | 835 | 470 | 0 |
| `url` | 0 | 0 | 0 |
| `profile_image_url` | 846 | 438 | 0 |
| `profile_image_url_https` | 833 | 442 | 0 |

### Count-field plausibility checks

| Column | Min | Max | Negative | Fractional |
|---|---:|---:|---:|---:|
| `statuses_count` | 0.0 | 5663.66450981619 | 0 | 937 |
| `followers_count` | 0.0 | 164.65134492879 | 0 | 900 |
| `friends_count` | 0.0 | 3541.65669877695 | 0 | 970 |
| `favourites_count` | 0.0 | 4415.4829979651 | 0 | 17 |
| `listed_count` | 0.0 | 2.25131015827703 | 0 | 2 |

### Other numeric-field checks

| Column | Min | Max | Non-finite | Outside 0-1 (boolean-like) | Fractional (boolean-like) |
|---|---:|---:|---:|---:|---:|
| `id` | 0.0 | 6535701770.48052 | 0 | n/a | n/a |
| `statuses_count` | 0.0 | 5663.66450981619 | 0 | n/a | n/a |
| `followers_count` | 0.0 | 164.65134492879 | 0 | n/a | n/a |
| `friends_count` | 0.0 | 3541.65669877695 | 0 | n/a | n/a |
| `favourites_count` | 0.0 | 4415.4829979651 | 0 | n/a | n/a |
| `listed_count` | 0.0 | 2.25131015827703 | 0 | n/a | n/a |
| `url` | 0.0 | 0.0 | 0 | n/a | n/a |
| `default_profile` | 0.0 | 5.86778556749169 | 0 | 629 | 954 |
| `default_profile_image` | 0.0 | 1.68053024139962 | 0 | 3 | 4 |
| `geo_enabled` | 0.0 | 1.67090744896536 | 0 | 1 | 1 |
| `profile_use_background_image` | 0.0 | 6.2370664255312 | 0 | 680 | 971 |
| `profile_background_tile` | 0.0 | 4.82981858523146 | 0 | 1 | 1 |
| `utc_offset` | 0.0 | 16636.5729872977 | 0 | n/a | n/a |
| `protected` | 0.0 | 0.0 | 0 | 0 | 0 |
| `verified` | 0.0 | 0.0 | 0 | 0 | 0 |
| `is_fake` | 1.0 | 1.0 | 0 | n/a | n/a |

Dataset-source values by label:

```json
{
  "<missing>": {
    "1": 691
  },
  "INT": {
    "1": 1307
  }
}
```

## real: `real_users training.xlsx`

- Rows: 1999
- Columns: 35
- Exact duplicate rows: 0
- Label distribution: `{'0': 1999}`
- Potential identifier columns found: `['id', 'screen_name', 'name', 'url', 'profile_image_url', 'profile_image_url_https', 'dataset']`

### Column types and missing values

| Column | Type | Missing | Unique non-missing |
|---|---:|---:|---:|
| `id` | float64 | 0 | 974 |
| `name` | str | 706 | 877 |
| `screen_name` | object | 652 | 879 |
| `statuses_count` | float64 | 0 | 984 |
| `followers_count` | float64 | 0 | 959 |
| `friends_count` | float64 | 0 | 993 |
| `favourites_count` | float64 | 0 | 861 |
| `listed_count` | float64 | 0 | 509 |
| `created_at` | str | 710 | 854 |
| `url` | str | 1583 | 279 |
| `lang` | str | 705 | 6 |
| `time_zone` | str | 1106 | 24 |
| `location` | str | 1110 | 409 |
| `default_profile` | float64 | 0 | 262 |
| `default_profile_image` | float64 | 0 | 2 |
| `geo_enabled` | float64 | 0 | 469 |
| `profile_image_url` | str | 717 | 850 |
| `profile_banner_url` | str | 1115 | 597 |
| `profile_use_background_image` | float64 | 0 | 909 |
| `profile_background_image_url_https` | str | 673 | 461 |
| `profile_text_color` | object | 687 | 110 |
| `profile_image_url_https` | str | 705 | 877 |
| `profile_sidebar_border_color` | object | 735 | 77 |
| `profile_background_tile` | float64 | 0 | 317 |
| `profile_sidebar_fill_color` | object | 684 | 116 |
| `profile_background_image_url` | str | 700 | 456 |
| `profile_background_color` | object | 692 | 170 |
| `profile_link_color` | object | 680 | 231 |
| `utc_offset` | float64 | 0 | 600 |
| `protected` | int64 | 0 | 1 |
| `verified` | int64 | 0 | 1 |
| `description` | str | 725 | 871 |
| `updated` | datetime64[us] | 697 | 1 |
| `dataset` | str | 715 | 1 |
| `is_fake` | int64 | 0 | 1 |

### Duplicate identifier diagnostics

| Column | Unique non-missing | Duplicate non-missing | Zero placeholders |
|---|---:|---:|---:|
| `id` | 973 | 0 | 1026 |
| `screen_name` | 879 | 468 | 0 |
| `name` | 874 | 419 | 0 |
| `url` | 279 | 137 | 0 |
| `profile_image_url` | 850 | 432 | 0 |
| `profile_image_url_https` | 877 | 417 | 0 |

### Count-field plausibility checks

| Column | Min | Max | Negative | Fractional |
|---|---:|---:|---:|---:|
| `statuses_count` | 0.0 | 139674.312061216 | 0 | 890 |
| `followers_count` | 0.0 | 71702.7306768701 | 0 | 947 |
| `friends_count` | 0.0 | 16878.4744842669 | 0 | 983 |
| `favourites_count` | 0.0 | 60892.1732803698 | 0 | 843 |
| `listed_count` | 0.0 | 915.626655197018 | 0 | 507 |

### Other numeric-field checks

| Column | Min | Max | Non-finite | Outside 0-1 (boolean-like) | Fractional (boolean-like) |
|---|---:|---:|---:|---:|---:|
| `id` | 0.0 | 5433508413.40916 | 0 | n/a | n/a |
| `statuses_count` | 0.0 | 139674.312061216 | 0 | n/a | n/a |
| `followers_count` | 0.0 | 71702.7306768701 | 0 | n/a | n/a |
| `friends_count` | 0.0 | 16878.4744842669 | 0 | n/a | n/a |
| `favourites_count` | 0.0 | 60892.1732803698 | 0 | n/a | n/a |
| `listed_count` | 0.0 | 915.626655197018 | 0 | n/a | n/a |
| `default_profile` | 0.0 | 5.86409759765352 | 0 | 164 | 261 |
| `default_profile_image` | 0.0 | 0.249336206469504 | 0 | 0 | 1 |
| `geo_enabled` | 0.0 | 6.44966764549292 | 0 | 315 | 468 |
| `profile_use_background_image` | 0.0 | 6.12497158988104 | 0 | 596 | 908 |
| `profile_background_tile` | 0.0 | 5.86908464306599 | 0 | 220 | 316 |
| `utc_offset` | 0.0 | 93605.2579012474 | 0 | n/a | n/a |
| `protected` | 0.0 | 0.0 | 0 | 0 | 0 |
| `verified` | 0.0 | 0.0 | 0 | 0 | 0 |
| `is_fake` | 0.0 | 0.0 | 0 | n/a | n/a |

Dataset-source values by label:

```json
{
  "<missing>": {
    "0": 715
  },
  "E13": {
    "0": 1284
  }
}
```

## test: `merged testing.xlsx`

- Rows: 1002
- Columns: 36
- Exact duplicate rows: 0
- Label distribution: `{'1': 502, '0': 500}`
- Potential identifier columns found: `['id', 'screen_name', 'name', 'url', 'profile_image_url', 'profile_image_url_https', 'dataset', 'RAND']`

### Column types and missing values

| Column | Type | Missing | Unique non-missing |
|---|---:|---:|---:|
| `id` | float64 | 0 | 486 |
| `name` | str | 340 | 596 |
| `screen_name` | str | 352 | 564 |
| `statuses_count` | float64 | 0 | 488 |
| `followers_count` | float64 | 0 | 455 |
| `friends_count` | float64 | 0 | 485 |
| `favourites_count` | float64 | 0 | 219 |
| `listed_count` | float64 | 0 | 130 |
| `created_at` | str | 334 | 598 |
| `url` | object | 404 | 84 |
| `lang` | str | 340 | 5 |
| `time_zone` | str | 783 | 13 |
| `location` | str | 458 | 412 |
| `default_profile` | float64 | 0 | 332 |
| `default_profile_image` | float64 | 0 | 3 |
| `geo_enabled` | float64 | 0 | 103 |
| `profile_image_url` | str | 382 | 539 |
| `profile_banner_url` | str | 778 | 202 |
| `profile_use_background_image` | float64 | 0 | 481 |
| `profile_background_image_url_https` | str | 347 | 147 |
| `profile_text_color` | object | 344 | 40 |
| `profile_image_url_https` | str | 355 | 572 |
| `profile_sidebar_border_color` | object | 361 | 39 |
| `profile_background_tile` | float64 | 0 | 79 |
| `profile_sidebar_fill_color` | object | 361 | 53 |
| `profile_background_image_url` | str | 345 | 158 |
| `profile_background_color` | object | 362 | 64 |
| `profile_link_color` | object | 326 | 76 |
| `utc_offset` | float64 | 0 | 153 |
| `protected` | int64 | 0 | 1 |
| `verified` | int64 | 0 | 1 |
| `description` | str | 390 | 537 |
| `updated` | datetime64[us] | 371 | 2 |
| `dataset` | str | 356 | 2 |
| `is_fake` | int64 | 0 | 2 |
| `RAND` | float64 | 0 | 1002 |

### Duplicate identifier diagnostics

| Column | Unique non-missing | Duplicate non-missing | Zero placeholders |
|---|---:|---:|---:|
| `id` | 485 | 0 | 517 |
| `screen_name` | 564 | 86 | 0 |
| `name` | 596 | 66 | 0 |
| `url` | 83 | 13 | 0 |
| `profile_image_url` | 539 | 81 | 0 |
| `profile_image_url_https` | 572 | 75 | 0 |

### Count-field plausibility checks

| Column | Min | Max | Negative | Fractional |
|---|---:|---:|---:|---:|
| `statuses_count` | 0.0 | 84730.1861406833 | 0 | 462 |
| `followers_count` | 0.0 | 33022.5618588138 | 0 | 452 |
| `friends_count` | 0.0 | 5359.31726076712 | 0 | 480 |
| `favourites_count` | 0.0 | 27858.6876731886 | 0 | 214 |
| `listed_count` | 0.0 | 234.890122176181 | 0 | 129 |

### Other numeric-field checks

| Column | Min | Max | Non-finite | Outside 0-1 (boolean-like) | Fractional (boolean-like) |
|---|---:|---:|---:|---:|---:|
| `id` | 0.0 | 5197951339.16782 | 0 | n/a | n/a |
| `statuses_count` | 0.0 | 84730.1861406833 | 0 | n/a | n/a |
| `followers_count` | 0.0 | 33022.5618588138 | 0 | n/a | n/a |
| `friends_count` | 0.0 | 5359.31726076712 | 0 | n/a | n/a |
| `favourites_count` | 0.0 | 27858.6876731886 | 0 | n/a | n/a |
| `listed_count` | 0.0 | 234.890122176181 | 0 | n/a | n/a |
| `default_profile` | 0.0 | 7.09454364954004 | 0 | 207 | 331 |
| `default_profile_image` | 0.0 | 2.24450848520812 | 0 | 1 | 2 |
| `geo_enabled` | 0.0 | 4.44021442598191 | 0 | 70 | 102 |
| `profile_use_background_image` | 0.0 | 5.90986551493018 | 0 | 329 | 480 |
| `profile_background_tile` | 0.0 | 3.79757626528014 | 0 | 59 | 78 |
| `utc_offset` | 0.0 | 93605.2579012474 | 0 | n/a | n/a |
| `protected` | 0.0 | 0.0 | 0 | 0 | 0 |
| `verified` | 0.0 | 0.0 | 0 | 0 | 0 |
| `is_fake` | 0.0 | 1.0 | 0 | n/a | n/a |
| `RAND` | 0.0009987243992354289 | 0.9979327234592771 | 0 | n/a | n/a |

Dataset-source values by label:

```json
{
  "<missing>": {
    "0": 187,
    "1": 169
  },
  "E13": {
    "0": 313,
    "1": 0
  },
  "INT": {
    "0": 0,
    "1": 333
  }
}
```

## Schema comparison

```json
{
  "training_match": true,
  "fake_only_columns": [],
  "real_only_columns": [],
  "test_only_columns_vs_training": [
    "RAND"
  ],
  "training_only_columns_vs_test": [],
  "training_dtype_mismatches": {
    "profile_sidebar_border_color": {
      "fake": "str",
      "real": "object"
    },
    "profile_sidebar_fill_color": {
      "fake": "str",
      "real": "object"
    },
    "screen_name": {
      "fake": "str",
      "real": "object"
    },
    "url": {
      "fake": "int64",
      "real": "str"
    }
  },
  "test_dtype_mismatches": {
    "profile_sidebar_border_color": {
      "training_fake": "str",
      "test": "object"
    },
    "profile_sidebar_fill_color": {
      "training_fake": "str",
      "test": "object"
    },
    "url": {
      "training_fake": "int64",
      "test": "object"
    }
  }
}
```

## Training/test overlap

```json
{
  "exact_records": 142,
  "fake_real_account_overlap": {
    "id": {
      "unique_fake": 978,
      "unique_real": 973,
      "unique_overlap": 0
    },
    "screen_name": {
      "unique_fake": 834,
      "unique_real": 879,
      "unique_overlap": 0
    },
    "profile_image_url_https": {
      "unique_fake": 833,
      "unique_real": 877,
      "unique_overlap": 1
    },
    "profile_image_url": {
      "unique_fake": 846,
      "unique_real": 850,
      "unique_overlap": 1
    },
    "name": {
      "unique_fake": 835,
      "unique_real": 874,
      "unique_overlap": 0
    }
  },
  "identifier_fields": {
    "id": {
      "unique_train": 1951,
      "unique_test": 485,
      "unique_overlap": 246,
      "test_rows_matching_train": 246
    },
    "screen_name": {
      "unique_train": 1713,
      "unique_test": 564,
      "unique_overlap": 459,
      "test_rows_matching_train": 532
    },
    "profile_image_url_https": {
      "unique_train": 1709,
      "unique_test": 572,
      "unique_overlap": 472,
      "test_rows_matching_train": 536
    },
    "profile_image_url": {
      "unique_train": 1695,
      "unique_test": 539,
      "unique_overlap": 441,
      "test_rows_matching_train": 507
    },
    "name": {
      "unique_train": 1709,
      "unique_test": 596,
      "unique_overlap": 474,
      "test_rows_matching_train": 529
    },
    "url": {
      "unique_train": 279,
      "unique_test": 83,
      "unique_overlap": 83,
      "test_rows_matching_train": 96
    }
  }
}
```

## Leakage and interpretation findings

- The requested merged testing(1).xlsx filename is absent; merged testing.xlsx is the only provided test workbook and is the one audited.
- The two training sources have no shared non-placeholder IDs or screen names; one profile image URL value is shared across each image URL field, which may be a common/default asset rather than the same account.
- The updated snapshot timestamp has one observed unique value per training source and is therefore excluded, along with created_at, to avoid deriving source-specific account-age features.
- Training dataset values are class-associated and must not be model features.
- The test workbook contains a RAND field; exclude it as a row-order/randomization artifact.
- Account identifiers, profile names, handles, URLs, and image URLs are excluded from model features.
- Test records overlap training records/accounts; test scores are not an independent generalization estimate.

## Limitations

Count fields contain fractional and zero-placeholder values, and many IDs are repeated or zero. These values are reported as supplied; no source value was silently repaired. `dataset` is a direct source proxy for the target, and `RAND` is excluded. Exact shared records and account-identifier overlap mean the requested test evaluation is contaminated by overlap and is reported with that limitation.
