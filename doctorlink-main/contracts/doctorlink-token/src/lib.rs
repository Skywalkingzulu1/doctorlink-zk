#![no_std]
use soroban_sdk::{
    contract, contractimpl, contracttype, symbol_short,
    Address, Env, String, Symbol,
};

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Balance(Address),
    State,
}

#[derive(Clone)]
#[contracttype]
pub struct TokenState {
    pub admin: Address,
    pub name: String,
    pub symbol: String,
    pub total_supply: i128,
}

const STATE_KEY: Symbol = symbol_short!("STATE");

#[contract]
pub struct DoctorLinkToken;

#[contractimpl]
impl DoctorLinkToken {
    pub fn initialize(env: Env, admin: Address, name: String, symbol: String) {
        let state = TokenState {
            admin: admin.clone(),
            name,
            symbol,
            total_supply: 0,
        };
        env.storage().instance().set(&STATE_KEY, &state);
        admin.require_auth();
    }

    pub fn name(env: Env) -> String {
        let state: TokenState = env.storage().instance().get(&STATE_KEY).unwrap();
        state.name
    }

    pub fn symbol(env: Env) -> String {
        let state: TokenState = env.storage().instance().get(&STATE_KEY).unwrap();
        state.symbol
    }

    pub fn total_supply(env: Env) -> i128 {
        let state: TokenState = env.storage().instance().get(&STATE_KEY).unwrap();
        state.total_supply
    }

    pub fn balance(env: Env, id: Address) -> i128 {
        env.storage()
            .persistent()
            .get(&DataKey::Balance(id))
            .unwrap_or(0)
    }

    pub fn transfer(env: Env, from: Address, to: Address, amount: i128) {
        from.require_auth();
        assert!(amount > 0, "amount must be positive");

        let from_bal = Self::balance(env.clone(), from.clone());
        assert!(from_bal >= amount, "insufficient balance");

        let to_bal = Self::balance(env.clone(), to.clone());

        env.storage()
            .persistent()
            .set(&DataKey::Balance(from), &(from_bal - amount));
        env.storage()
            .persistent()
            .set(&DataKey::Balance(to), &(to_bal + amount));
    }

    pub fn reward_health(env: Env, admin: Address, patient: Address, amount: i128) {
        admin.require_auth();
        assert!(amount > 0, "amount must be positive");

        let mut state: TokenState = env.storage().instance().get(&STATE_KEY).unwrap();
        assert!(admin == state.admin, "only admin can reward");

        let bal = Self::balance(env.clone(), patient.clone());
        env.storage()
            .persistent()
            .set(&DataKey::Balance(patient), &(bal + amount));
        state.total_supply += amount;
        env.storage().instance().set(&STATE_KEY, &state);
    }
}
