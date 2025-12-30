# Changelog

## Unreleased

+ Update `--paging` option to `--no-pager` and honor $PAGER to be more Unix-like
+ Print placeholders for non-text cell output (images and javascript), pretty prints specific text types (latex, json, html)
+ Remove cell borders to be copy-paste friendly

## 0.1.2dev1 (Mar 7, 2024)

+ Fixed word wrap in code cells. Closes [Text wrapping for code cells #1](https://github.com/tnwei/nbread/issues/1)

## 0.1.1 (Mar 7, 2024)

+ Changed `--pager` option which toggles on/off pager to `--paging=[auto/never/always]`. Default is auto. Closes [Automatically pipe to pager as required #3](https://github.com/tnwei/nbread/issues/3)

## 0.1.0

Initial release
