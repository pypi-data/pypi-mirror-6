#!/usr/bin/python
# -*- coding: utf-8 -*-

import info
import migration

def run_help():
    print "%s %s (%s)" % (info.NAME, info.VERSION, info.AUTHOR)
    print ""
    print "The most commonly used migratore commands are:"
    print "  version          Prints the current version of migratore"
    print "  list             Lists the executed migrations on the current database"
    print "  apply [path]     Executes the pending migrations using the defined directory or current"
    print "  generates [path] Generates a new migration file into the target path"

def run_version():
    print "%s %s" % (info.NAME, info.VERSION)

def run_list():
    migration.Migration.list()

def run_apply(path = None):
    migration.Migration.apply(path)

def run_generate(path = None):
    migration.Migration.generate(path)

run_list()
