# ──────────────────────────────────────────────
# RECIPE MANAGER
# ──────────────────────────────────────────────

class RecipeManager:
    @staticmethod
    def find_duplicate_content(recipe_data, simulations):
        """Return the recipe name if duplicate content exists, otherwise None."""
        for sim_name, sim_data in simulations.items():
            match = all(
                sim_data.get(k) == v
                for k, v in recipe_data.items() if k != "Name"
            ) and all(
                k == "Name" or k in recipe_data
                for k in sim_data.keys()
            )
            if match:
                return sim_name
        return None
