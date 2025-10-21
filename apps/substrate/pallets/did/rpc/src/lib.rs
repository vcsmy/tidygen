//! RPC interface for the DID pallet

use codec::Codec;
use jsonrpsee::{
    core::{async_trait, RpcResult},
    proc_macros::rpc,
    types::error::{CallError, ErrorCode, ErrorObject},
};
use sp_api::ProvideRuntimeApi;
use sp_blockchain::HeaderBackend;
use sp_runtime::traits::Block as BlockT;
use std::sync::Arc;

pub use pallet_did_runtime_api::DidApi as DidRuntimeApi;

#[rpc(client, server)]
pub trait DidApi<BlockHash, AccountId, DidDocument> {
    /// Get DID document for an account
    #[method(name = "did_getDid")]
    fn get_did(
        &self,
        account: AccountId,
        at: Option<BlockHash>,
    ) -> RpcResult<Option<DidDocument>>;

    /// Get account from DID identifier
    #[method(name = "did_getAccountFromDid")]
    fn get_account_from_did(
        &self,
        did_identifier: String,
        at: Option<BlockHash>,
    ) -> RpcResult<Option<AccountId>>;

    /// Check if DID is active
    #[method(name = "did_isDidActive")]
    fn is_did_active(&self, account: AccountId, at: Option<BlockHash>) -> RpcResult<bool>;

    /// Get total DID count
    #[method(name = "did_getTotalDids")]
    fn get_total_dids(&self, at: Option<BlockHash>) -> RpcResult<u64>;
}

/// A struct that implements the `DidApi`.
pub struct Did<C, Block> {
    client: Arc<C>,
    _marker: std::marker::PhantomData<Block>,
}

impl<C, Block> Did<C, Block> {
    /// Create new `Did` instance with the given reference to the client.
    pub fn new(client: Arc<C>) -> Self {
        Self {
            client,
            _marker: Default::default(),
        }
    }
}

#[async_trait]
impl<C, Block, AccountId, DidDocument>
    DidApiServer<<Block as BlockT>::Hash, AccountId, DidDocument> for Did<C, Block>
where
    Block: BlockT,
    C: Send + Sync + 'static + ProvideRuntimeApi<Block> + HeaderBackend<Block>,
    C::Api: DidRuntimeApi<Block, AccountId, DidDocument>,
    AccountId: Codec,
    DidDocument: Codec,
{
    fn get_did(
        &self,
        account: AccountId,
        at: Option<<Block as BlockT>::Hash>,
    ) -> RpcResult<Option<DidDocument>> {
        let api = self.client.runtime_api();
        let at = at.unwrap_or_else(|| self.client.info().best_hash);

        api.get_did(at, account).map_err(runtime_error_into_rpc_err)
    }

    fn get_account_from_did(
        &self,
        did_identifier: String,
        at: Option<<Block as BlockT>::Hash>,
    ) -> RpcResult<Option<AccountId>> {
        let api = self.client.runtime_api();
        let at = at.unwrap_or_else(|| self.client.info().best_hash);

        api.get_account_from_did(at, did_identifier.as_bytes().to_vec())
            .map_err(runtime_error_into_rpc_err)
    }

    fn is_did_active(
        &self,
        account: AccountId,
        at: Option<<Block as BlockT>::Hash>,
    ) -> RpcResult<bool> {
        let api = self.client.runtime_api();
        let at = at.unwrap_or_else(|| self.client.info().best_hash);

        api.is_did_active(at, account)
            .map_err(runtime_error_into_rpc_err)
    }

    fn get_total_dids(&self, at: Option<<Block as BlockT>::Hash>) -> RpcResult<u64> {
        let api = self.client.runtime_api();
        let at = at.unwrap_or_else(|| self.client.info().best_hash);

        api.get_total_dids(at).map_err(runtime_error_into_rpc_err)
    }
}

/// Converts a runtime trap into an RPC error.
fn runtime_error_into_rpc_err(err: impl std::fmt::Debug) -> ErrorObject<'static> {
    CallError::Custom(ErrorCode::InternalError.into())
        .into()
}

