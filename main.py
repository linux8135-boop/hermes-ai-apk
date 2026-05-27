"""Hermes AI — Android entry point. Starts foreground service."""
import sys
import os

SERVICE_NAME = "HermesGateway"


def start_service():
    try:
        from android import AndroidService
        service = AndroidService(SERVICE_NAME, "Hermes AI active")
        service.start("")
    except ImportError:
        pass


start_service()
