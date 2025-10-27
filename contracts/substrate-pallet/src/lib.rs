//! A FRAME pallet skeleton that stores service verification hashes and manages escrow-like balances.
//! This scaffold is intended as a starting point (Level 2 -> Level 3 path). It provides storage, events and dispatchable calls.

#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        pallet_prelude::*,
        traits::{Currency, ExistenceRequirement::AllowDeath, ReservableCurrency},
    };
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;

    // Configure the pallet by specifying the parameters and types on which it depends.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The event type.
        type Event: From<Event<Self>> + IsType<<Self as frame_system::Config>::Event>;
        /// The currency type (for escrow).
        type Currency: Currency<Self::AccountId> + ReservableCurrency<Self::AccountId>;
        /// Weight info placeholder
        type WeightInfo: Get<u64>;
    }

    // Pallet storage items.
    #[pallet::storage]
    #[pallet::getter(fn service_data)]
    pub type ServiceData<T: Config> = StorageMap<_, Blake2_128Concat, u64, Vec<u8>, OptionQuery>;

    #[pallet::storage]
    #[pallet::getter(fn escrow)]
    pub type Escrow<T: Config> = StorageMap<_, Blake2_128Concat, u64, BalanceOf<T>, ValueQuery>;

    #[pallet::type_value]
    pub fn DefaultForBool() -> bool { false }

    // Type alias for balances
    pub type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ServiceStored(u64, T::AccountId),
        EscrowDeposited(u64, BalanceOf<T>, T::AccountId),
        EscrowReleased(u64, BalanceOf<T>, T::AccountId),
    }

    #[pallet::error]
    pub enum Error<T> {
        ServiceAlreadyExists,
        ServiceNotFound,
        NoEscrowBalance,
        NotAuthorized,
    }

    #[pallet::pallet]
    #[pallet::generate_store(pub(super) trait Store)]
    pub struct Pallet<T>(_);

    // Genesis config - optional
    #[pallet::genesis_config]
    pub struct GenesisConfig<T: Config> {
        pub dummy: Option<u64>,
        pub _phantom: sp_std::marker::PhantomData<T>,
    }

    #[cfg(feature = "std")]
    impl<T: Config> Default for GenesisConfig<T> {
        fn default() -> Self { Self { dummy: None, _phantom: Default::default() } }
    }

    #[pallet::call]
    impl<T:Config> Pallet<T> where T::AccountId: AsRef<[u8]> {
        /// Store verification data (service_id -> data_hash)
        #[pallet::weight(10_000)]
        pub fn store(origin: OriginFor<T>, service_id: u64, data: Vec<u8>) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(!ServiceData::<T>::contains_key(&service_id), Error::<T>::ServiceAlreadyExists);
            ServiceData::<T>::insert(&service_id, data);
            Self::deposit_event(Event::ServiceStored(service_id, who));
            Ok(())
        }

        /// Deposit escrow (in native currency) for a service
        #[pallet::weight(10_000)]
        pub fn deposit_escrow(origin: OriginFor<T>, service_id: u64, #[pallet::compact] amount: BalanceOf<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;
            // transfer from caller to pallet account (reserve or transfer)
            let pallet_account = <Pallet<T> as Pallet<T>>::account_id();
            T::Currency::transfer(&who, &pallet_account, amount, AllowDeath)?;
            let prev = Escrow::<T>::get(&service_id);
            Escrow::<T>::insert(&service_id, prev + amount);
            Self::deposit_event(Event::EscrowDeposited(service_id, amount, who));
            Ok(())
        }

        /// Release escrow to a beneficiary — restricted to Root/origin (or later multisig/Governance)
        #[pallet::weight(10_000)]
        pub fn release_escrow(origin: OriginFor<T>, service_id: u64, to: T::AccountId, #[pallet::compact] amount: BalanceOf<T>) -> DispatchResult {
            ensure_root(origin)?; // for POC, require Root. Replace with governance/multisig later.
            let pallet_account = <Pallet<T> as Pallet<T>>::account_id();
            let balance = Escrow::<T>::get(&service_id);
            ensure!(balance >= amount, Error::<T>::NoEscrowBalance);
            Escrow::<T>::insert(&service_id, balance - amount);
            T::Currency::transfer(&pallet_account, &to, amount, AllowDeath)?;
            Self::deposit_event(Event::EscrowReleased(service_id, amount, to));
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        /// Simple derived account id for the pallet (using pallet id pattern)
        pub fn account_id() -> T::AccountId {
            // For example purposes: use a deterministic account id derivation
            // In production use PalletId or similar
            let entropy = b"tidygen_escrow";
            T::AccountId::decode(&mut &sp_io::hashing::blake2_256(entropy)[..]).unwrap_or_default()
        }
    }

    // weight info stub
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}
}