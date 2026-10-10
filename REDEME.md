# Crag Sun-Exposure Calculator 🧗‍♂️☀️

A Python-based CLI tool and upcoming web app to calculate exact solar illumination hours for climbing crags and vertical walls.

## Features
- Calculates precise solar position (azimuth and zenith) using `pvlib`.
- Determines wall illumination taking into account wall aspect (0°-360°) and angular solar offset.
- Automatically resolves local timezones based on coordinates using `tzfpy`.
- Command-line interface for rapid testing.