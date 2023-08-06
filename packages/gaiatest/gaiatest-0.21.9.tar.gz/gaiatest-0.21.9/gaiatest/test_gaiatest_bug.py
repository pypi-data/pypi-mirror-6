import gaiatest
import marionette

mari = marionette.Marionette()
mari.start_session()
apps = gaiatest.GaiaApps(mari)

# gaiatest bug
print apps.running_apps
apps.launch('browser', switch_to_frame=False)
print apps.running_apps  # fails
