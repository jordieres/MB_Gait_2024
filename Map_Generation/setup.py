# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:07:28 2024

@author: marbo
"""

from setuptools import setup, find_packages

setup(
    name='tfm_sclerosis',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'folium',
        'plotly',
        'influxdb-client',
        'toml'
    ],
    entry_points={
        'console_scripts': [
            'tfm_sclerosis=tfm_sclerosis.main:main',
        ],
    },
)
