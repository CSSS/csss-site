#!/bin/bash


ssh csss@sfucsss.org "rm -fr /home/csss/csss-site"
scp -r * csss@sfucsss.org:/home/csss/csss-site/
