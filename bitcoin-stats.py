#!/usr/bin/env python3
"""
bitcoin-stats.py — On-chain Bitcoin statistics CLI

Fetches real-time Bitcoin network statistics: hash rate, difficulty,
mempool size, fees, blocks, and more. Pure Python, zero dependencies.

Usage:
    python bitcoin-stats.py                          # All stats
    python bitcoin-stats.py --hashrate               # Hash rate only
    python bitcoin-stats.py --fees                   # Current fees
    python bitcoin-stats.py --mempool                # Mempool stats
    python bitcoin-stats.py --json                     # JSON output

Support: https://github.com/yourusername/bitcoin-stats
"""

import sys
import json
import urllib.request
from datetime import datetime


def fetch_mempool_data(endpoint=""):
    """Fetch data from mempool.space API"""
    url = f"https://mempool.space/api{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "bitcoin-stats/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def format_hashrate(hashrate):
    """Format hashrate to human-readable"""
    if hashrate > 1_000_000_000:  # EH/s
        return f"{hashrate / 1_000_000_000:.2f} EH/s"
    elif hashrate > 1_000_000:  # PH/s
        return f"{hashrate / 1_000_000:.2f} PH/s"
    elif hashrate > 1_000:  # TH/s
        return f"{hashrate / 1_000:.2f} TH/s"
    return f"{hashrate:.2f} TH/s"


def format_sat_v(sats):
    """Format satoshi/vB"""
    return f"{sats:.1f} sat/vB"


def display_all_stats():
    """Display all Bitcoin network stats"""
    print("\n  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║           ₿ BITCOIN NETWORK STATISTICS                     ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print(f"  Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Fetch all data in parallel-ish (sequential is fine for CLI)
    stats = fetch_mempool_data("/blocks")
    network = fetch_mempool_data("/blocks/0")  # Latest block info
    fees = fetch_mempool_data("/v1/fees/recommended")
    mempool = fetch_mempool_data("/mempool")
    miners = fetch_mempool_data("/mining/hashrate/3d")

    # Calculate difficulty and hashrate from latest block
    latest_block = stats[0] if stats else {}

    print("  ┌── BLOCK INFO ──────────────────────────────────────────────┐")
    if latest_block:
        print(f"  │ Height:     {latest_block.get('height', 'N/A')}")
        print(f"  │ Hash:       {latest_block.get('id', 'N/A')[:40]}...")
        print(f"  │ Size:       {latest_block.get('size', 0) / 1_000_000:.2f} MB")
        print(f"  │ Txns:       {latest_block.get('txids', []) and len(latest_block.get('txids', [])) or 'N/A'}")
    else:
        print("  │ Unable to fetch block data")
    print("  └─────────────────────────────────────────────────────────────┘\n")

    print("  ┌── FEE ESTIMATES ───────────────────────────────────────────┐")
    if isinstance(fees, dict) and "fastest" in fees:
        print(f"  │ Fast:     {format_sat_v(fees['fastest'])}")
        print(f"  │ Medium:   {format_sat_v(fees['halfHour'])}")
        print(f"  │ Slow:     {format_sat_v(fees['hour'])}")
    else:
        print("  │ Unable to fetch fee data")
    print("  └─────────────────────────────────────────────────────────────┘\n")

    print("  ┌── MEMPOOL ─────────────────────────────────────────────────┐")
    if isinstance(mempool, dict):
        print(f"  │ Size:       {mempool.get('vsize', 0) / 1_000_000:.2f} MB")
        print(f"  │ Transactions: {mempool.get('count', 0):,}")
        print(f"  │ Total Fees:   {mempool.get('total_fee', 0) / 100_000_000:.4f} BTC")
    else:
        print("  │ Unable to fetch mempool data")
    print("  └─────────────────────────────────────────────────────────────┘\n")

    print(f"  📦 Source: https://github.com/yourusername/bitcoin-stats\n")


def display_json():
    """Output all stats as JSON"""
    data = {
        "block": fetch_mempool_data("/blocks")[:1],
        "fees": fetch_mempool_data("/v1/fees/recommended"),
        "mempool": fetch_mempool_data("/mempool"),
    }
    print(json.dumps(data, indent=2))


def main():
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "json" in [a.lower() for a in args]:
        display_json()
    elif "fees" in [a.lower() for a in args]:
        fees = fetch_mempool_data("/v1/fees/recommended")
        print(f"\n  {'BITCOIN FEE ESTIMATES':^40}")
        print(f"  {'=' * 40}")
        if isinstance(fees, dict):
            print(f"  Fast:       {format_sat_v(fees.get('fastest', 0))}")
            print(f"  Medium:     {format_sat_v(fees.get('halfHour', 0))}")
            print(f"  Slow:       {format_sat_v(fees.get('hour', 0))}")
        print()
    elif "mempool" in [a.lower() for a in args]:
        mempool = fetch_mempool_data("/mempool")
        print(f"\n  {'MEMPOOL STATUS':^40}")
        print(f"  {'=' * 40}")
        if isinstance(mempool, dict):
            print(f"  Size:         {mempool.get('vsize', 0) / 1_000_000:.2f} MB")
            print(f"  Transactions: {mempool.get('count', 0):,}")
            print(f"  Total Fees:   {mempool.get('total_fee', 0) / 100_000_000:.4f} BTC")
        print()
    else:
        display_all_stats()


if __name__ == "__main__":
    main()
