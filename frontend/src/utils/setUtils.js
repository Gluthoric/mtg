import axios from "axios";

export const fetchSetDetails = async (setCode) => {
  try {
    const response = await axios.get(`/api/sets/${setCode}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching set details:", error);
    throw error;
  }
};

export const applyFilters = (cards, filters) => {
  return cards.filter((card) => {
    if (
      filters.name &&
      !card.name.toLowerCase().includes(filters.name.toLowerCase())
    )
      return false;
    if (filters.rarities.length && !filters.rarities.includes(card.rarity))
      return false;
    if (
      filters.colors.length &&
      !filters.colors.every((color) => card.colors.includes(color))
    )
      return false;
    if (
      filters.missing &&
      (card.quantity_regular > 0 || card.quantity_foil > 0)
    )
      return false;
    if (
      filters.types.length &&
      !filters.types.some((type) =>
        card.type_line.toLowerCase().includes(type.toLowerCase()),
      )
    )
      return false;
    if (filters.keyword && !card.keywords.includes(filters.keyword))
      return false;
    return true;
  });
};
