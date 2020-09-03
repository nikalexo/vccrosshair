# vccrosshair

This is a CLI for a classifier I wrote as part of my Bachelor Thesis. This tool can to an extent distinguish between commits that are prone to be vulnerable and ones that are not. You can find the entire thesis as well as a summary in the Thesis directory.

## Table of Contents
- [Installation](#installation)
- [Example](#example)
- [Dataset](#dataset)

## Installation
```
pip3 install -r requirements.txt
```

## Example
In this example we run the classifier over the commit that introduced the infamous heartbleed bug.
```
vccrosshair --repo openssl --commit 4817504d069b4c5082161b02a22116ad75f822b1
> Commit is prone to be vulnerable!
> Confidence: 0.6815684510145337
> The most significant feature was: Average added line count (per file count)
```
## Dataset
The dataset the classifier was trained on is soon to be released along with a paper that dives deep into its creation. I will link to it here upon release!
