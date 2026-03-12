// Keep CRA production builds from failing on pre-existing lint warnings in CI.
process.env.CI = 'false';

require('react-scripts/scripts/build');
