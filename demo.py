from __future__ import annotations


def summarize_numbers(values: list[float]) -> dict[str, float]:
    if not values:
        return {"count": 0, "total": 0.0, "average": 0.0}
    total = sum(values)
    return {"count": len(values), "total": total, "average": total / len(values)}


if __name__ == "__main__":
    print(summarize_numbers([1, 2, 3, 5, 8]))

