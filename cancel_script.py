import asyncio
from pythereum import TitanBuilder, BuilderRPC

# ========================================
# CONFIGURATION - Edit these values
# ========================================

# Transaction hash to cancel (the hash returned by send_private_transaction)
TX_HASH_TO_CANCEL = "0x..."

# ========================================
# Main Function
# ========================================

async def cancel_transaction(tx_hash):
    """
    Cancel a private transaction that was sent to Titan Builder.
    
    Args:
        tx_hash: The transaction hash to cancel
    
    Returns:
        Result of the cancellation attempt
    """
    print("=" * 60)
    print("TITAN BUILDER - CANCEL TRANSACTION")
    print("=" * 60)
    print(f"Transaction to cancel: {tx_hash}")
    print("=" * 60)
    
    async with BuilderRPC(TitanBuilder()) as client:
        print("\n📤 Sending cancellation request...")
        
        try:
            # Attempt to cancel the transaction
            result = await client.cancel_private_transaction(tx_hash)
            
            print("\n" + "=" * 60)
            print("CANCELLATION RESULT")
            print("=" * 60)
            print(f"✓ Success! Result: {result}")
            print("\nNote: This cancels the transaction with the builder,")
            print("but if it was already included in a block, the")
            print("cancellation won't have any effect.")
            
            return result
            
        except Exception as e:
            print("\n" + "=" * 60)
            print("CANCELLATION FAILED")
            print("=" * 60)
            print(f"✗ Error: {e}")
            print("\nPossible reasons:")
            print("  - Transaction already included in a block")
            print("  - Invalid transaction hash")
            print("  - Transaction not found in builder's mempool")
            print("  - Transaction already executed or failed")
            
            return None


async def main():
    """Main entry point for the script."""
    
    # Validate transaction hash format
    if TX_HASH_TO_CANCEL == "0x..." or not TX_HASH_TO_CANCEL.startswith("0x"):
        print("⚠ ERROR: Please set TX_HASH_TO_CANCEL to a valid transaction hash!")
        print("Example: TX_HASH_TO_CANCEL = '0x1234567890abcdef...'")
        return
    
    # Cancel the transaction
    result = await cancel_transaction(TX_HASH_TO_CANCEL)
    
    if result:
        print("\n✓ Transaction cancellation completed successfully!")
    else:
        print("\n✗ Transaction cancellation failed. See error above.")


if __name__ == "__main__":
    asyncio.run(main())

