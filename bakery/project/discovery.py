def discover_license(contents):
    copyright_license = ''
    if contents.find('OPEN FONT LICENSE Version 1.1'):
        copyright_license = 'ofl'
    elif contents.find('Apache License, Version 2.0'):
        copyright_license = 'apache'
    elif contents.find('UBUNTU FONT LICENCE Version 1.0'):
        copyright_license = 'ufl'
    return copyright_license
