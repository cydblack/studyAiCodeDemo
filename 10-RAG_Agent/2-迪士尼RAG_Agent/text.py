#!/usr/bin/env python
# coding: utf-8
import os

print(os.path.abspath(__file__))
print(os.path.dirname(os.path.abspath(__file__)))
print(os.path.join(os.path.dirname(__file__), "12", "car.mp4"))
print(os.path.dirname(__file__))
