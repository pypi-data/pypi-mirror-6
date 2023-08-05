  var path_location = location.pathname.replace(/\/[^/]+$/, '');
  path_location = '/Plone/portal_javascripts/BISETheme/++resource++bise.biodiversityfactsheet/';
  var dojoConfig = {
    parseOnLoad: true,
    packages: [ { 
        name: "utilities",
        location: path_location
      },{
        name: "templateConfig",
        location: path_location 
      }
    ]
  };

