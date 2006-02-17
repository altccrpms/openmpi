# Makefile for source rpm: openmpi
# $Id$
NAME := openmpi
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
