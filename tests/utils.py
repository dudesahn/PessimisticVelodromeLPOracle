import pytest
import brownie
from brownie import interface, chain

# returns (profit, loss) of a harvest
def harvest_strategy(yswaps_profit, strategy, token, gov, profit_whale, profit_amount, destination_strategy):
    
    # reset everything with a sleep and mine
    chain.sleep(1)
    chain.mine(1)
    
    # add in any custom logic needed here, for instance with router strategy
    token.transfer(destination_strategy, profit_amount, {"from": profit_whale})
    destination_strategy.setDoHealthCheck(False, {"from": gov})
    destination_strategy.harvest({"from": gov})
    chain.mine(1)
    chain.sleep(86400 * 5)
    
    # if using yswaps, we need to donate profit to our strategy from our profit whale
    if yswaps_profit:
        token.transfer(strategy, profit_amount, {"from": profit_whale})
        
    tx = strategy.harvest({"from": gov})
    profit = tx.events["Harvested"]["profit"] / (10 ** token.decimals())
    loss = tx.events["Harvested"]["loss"] / (10 ** token.decimals())
    
    # assert there are no loose funds in strategy after a harvest
    assert strategy.balanceOfWant() == 0
    
    # reset everything with a sleep and mine
    chain.sleep(1)
    chain.mine(1)
    
    # return our profit, loss
    return (profit, loss)