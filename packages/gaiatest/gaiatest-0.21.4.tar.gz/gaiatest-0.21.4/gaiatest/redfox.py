#!/usr/bin/env python

import os
import time

from gaiatest.apps.contacts.app import Contacts
from gaiatest.gaia_test import GaiaApps
from gaiatest.gaia_test import GaiaData
from gaiatest.gaia_test import LockScreen
from marionette import Marionette


def main():
    capture = False
    marionette = Marionette()
    marionette.start_session()
    LockScreen(marionette).unlock()
    GaiaData(marionette).set_setting('screen.brightness', 1)
    apps = GaiaApps(marionette)
    apps.kill_all()
    contacts = Contacts(marionette)
    contacts.launch()
    new_contact = contacts.tap_new_contact()
    if capture:
        import videocapture
        capture_controller = videocapture.CaptureController('pointgrey', capture_area=[321, 54, 953, 959])
        capture_file = os.path.join(os.path.dirname(__file__), '../captures', 'capture-keyboard-%s.zip' % time.time())
        capture_controller.start_capture(capture_file)
        start_frame = capture_controller.capture_framenum()
    marionette.find_element(*new_contact._given_name_locator).tap()
    while not new_contact.keyboard.is_displayed():
        time.sleep(0.5)
    new_contact.keyboard.send('red fox runs fast')
    marionette.delete_session()
    if capture:
        end_frame = capture_controller.capture_framenum()
        capture_controller.terminate_capture()
        capture_controller.convert_capture(start_frame, end_frame)

main()