#!/usr/bin/env python
import os
import sys

def evaluate_context(*args, **kwargs):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monscale.settings")

    from django.core.management import call_command

    call_command("evaluate_context", sys.argv)