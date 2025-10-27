import { ApiPromise, WsProvider } from '@polkadot/api';
import { ContractPromise } from '@polkadot/api-contract';
import { hexToU8a, stringToHex } from '@polkadot/util';

export async function createApi(wsEndpoint = 'ws://127.0.0.1:9944') {
  const provider = new WsProvider(wsEndpoint);
  const api = await ApiPromise.create({ provider });
  return api;
}

/**
 * Deploy a contract using existing metadata and wasm via a relayer or JS deploy flow.
 * (This SDK focuses on interaction; deployment is expected to be done via backend scripts.)
 */
export function contractInstance(api: ApiPromise, metadata: any, address: string) {
  return new ContractPromise(api, metadata, address);
}

export async function store(api: ApiPromise, metadata: any, address: string, signer: any, serviceId: number, payload: string) {
  const contract = contractInstance(api, metadata, address);
  const dataHash = stringToHex(payload); // contract expects bytes; choose your encoding strategy
  const tx = contract.tx.store({ gasLimit: -1, value: 0 }, serviceId, dataHash);
  const unsub = await tx.signAndSend(signer, (result) => {
    if (result.status.isInBlock) {
      console.log('In block', result.status.asInBlock.toHex());
    } else if (result.status.isFinalized) {
      console.log('Finalized', result.status.asFinalized.toHex());
      unsub();
    }
  });
}