#!/bin/bash

wait-for-it -t 30 redis:6379

exec "$@"