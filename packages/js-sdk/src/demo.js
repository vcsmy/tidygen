// Node demo for tidygen-js-sdk
const fs = require('fs');
const path = require('path');
const { createApi, contractInstance } = require('../dist');

async function run() {
  const api = await createApi();
  const metadata = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../../contracts/substrate-poc/target/ink/metadata.json'), 'utf8'));
  const contractAddress = process.argv[2];
  if (!contractAddress) {
    console.error('Usage: node demo.js <contractAddress>');
    process.exit(2);
  }
  const contract = contractInstance(api, metadata, contractAddress);
  console.log('Contract instance ready:', contract.address.toString());
  process.exit(0);
}

run().catch(console.error);