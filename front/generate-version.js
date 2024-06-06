const fs = require('fs');
const path = require('path');
require('dotenv').config();

const version = process.env.VITE_VERSION_DATE_TIME;

const versionData = {
    version_date_time: version
};

const outputPath = path.resolve(__dirname, 'public/version.json');

fs.writeFileSync(outputPath, JSON.stringify(versionData, null, 2), 'utf8');

console.log(`version.json criado com a versão ${version}`);
