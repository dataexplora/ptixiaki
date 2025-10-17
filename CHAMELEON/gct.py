from itertools import permutations

CONSONANCE_VECTOR = [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0]  # GCT consonance rules

def is_consonant(interval):
    """Checks if an interval is consonant based on the GCT consonance vector."""
    return CONSONANCE_VECTOR[interval % 12] == 1

def find_maximal_consonant_subset(chord):
    """Finds the largest subset of consonant tones."""
    best_subset = []
    for perm in permutations(chord):
        subset = [perm[0]]
        for note in perm[1:]:
            if all(is_consonant(abs(note - s)) for s in subset):
                subset.append(note)
        if len(subset) > len(best_subset):
            best_subset = subset
    return sorted(best_subset)

def determine_root(chord):
    """Determines the root based on the lowest note of the maximal consonant subset."""
    consonant_subset = find_maximal_consonant_subset(chord)
    return min(consonant_subset)  # Root is the lowest note in the base

def normalize_to_root(chord, root):
    """Transposes the chord so that the root becomes 0 while maintaining intervallic relationships."""
    return sorted([(note - root) % 12 for note in chord])

def get_scale_degree(root, scale):
    """Finds the correct scale degree of the chord's root relative to the scale root."""
    scale_root, scale_vector = scale
    
    # Compute the relative position of the root within the scale
    scale_degrees = [(note - scale_root) % 12 for note in scale_vector]
    
    if root in scale_vector:
        return scale_degrees[scale_vector.index(root)]  # Direct match
    else:
        # Approximate to the closest numeric match in the scale system
        closest_scale_degree = min(scale_degrees, key=lambda x: abs(x - (root - scale_root) % 12))
        return closest_scale_degree


def gct_encode(chord, scale):
    """Encodes the chord in GCT format with correct scale-relative positioning."""
    scale_root, scale_vector = scale  # Extract scale root and scale type
    root = determine_root(chord)

    # Compute the scale degree where the chord belongs
    scale_degree = get_scale_degree(root, scale_vector)

    # Transpose all tones so the root becomes 0 while keeping chromatic tones unchanged
    normalized_chord = sorted([(note - root) % 12 for note in chord])

    return [scale_degree, normalized_chord]


# Test the function
chord = [1, 4, 7, 9]  
scale = [4, [0, 2, 4, 5, 7, 9, 11]]  
encoding = gct_encode(chord, scale)
encoding
