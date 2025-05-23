SIMILARITY_PROMPT = """
    You are an expert Quality Assurance (QA) specialist for product image generation. Your task is to meticulously compare two images of a product:

    1.  **[IMAGE 1]: The Original Studio Product Photo** (A high-fidelity, pristine image of the product taken in a controlled environment.)
    2.  **[IMAGE 2]: The AI-Generated Scene Photo** (An image where the product from the studio photo has been integrated into a real-world or composite scene by an AI model.)

    **Objective:**
    The AI model has a known tendency to inadvertently distort, modify, or misrepresent the product during integration, which is **not desired**. Your primary objective is to assess the fidelity of the product rendering in the AI-generated scene photo against the original studio photograph. You must identify any discrepancies, no matter how subtle.

    **Evaluation Criteria:**
    Evaluate the product within the AI-generated scene based on the following crucial aspects, comparing them directly to the original studio photo:

    *   **(a) Color Accuracy:** How precisely do the colors (hues, saturation, brightness) of the product match the original? Look for any shifts, fading, or over-saturation.
    *   **(b) Geometric Fidelity:** Is the size, shape, proportions, and overall outline of the product identical? Identify any stretching, squashing, distortion, missing parts, or added elements. This includes maintaining the correct perspective and angles.
    *   **(c) Texture & Material Reproduction:** Does the texture (e.g., glossy, matte, rough, smooth, fabric weave) accurately reflect the original material properties? Are reflections, shadows, and surface details consistent?
    *   **(d) Detail Preservation:** Are fine details, logos, text, small features, and ornamentation perfectly rendered, sharp, and legible as in the original? Note any blurring, simplification, or loss of intricate details.

    **Scoring:**
    Assign an overall similarity score between **0.0 and 1.0**, where:
    *   `1.0`: A perfect, indistinguishable match in all aspects. The AI-generated product is flawless compared to the original.
    *   `0.0`: A complete mismatch, severe distortion, the product is entirely unrecognizable, or completely missing from the AI-generated photo.
    *   Intermediate scores should reflect the degree of deviation across the evaluated criteria. Minor discrepancies will result in scores closer to 1.0, while significant flaws will push the score closer to 0.0.

    **Output Format:**
    Your output MUST be a flat JSON object with single-level entries. Dont give any explanations, only return the metric values.
    
    ```json
    {
    "overall_match_score": 0.X,
    "color_accuracy_score": 0.X,          // Score for color fidelity (0.0-1.0)
    "geometric_fidelity_score": 0.X,      // Score for shape, size, proportions (0.0-1.0)
    "texture_reproduction_score": 0.X,    // Score for material and surface appearance (0.0-1.0)
    "detail_preservation_score": 0.X,     // Score for fine features, logos, text (0.0-1.0)
    }
    """

STYLE_PROMPT = """
    **Objective:** Analyze the provided image(s) and generate a detailed textual style guide capturing their 
    core visual characteristics. This style guide will be used later to generate new background images in a 
    similar style, specifically for a retail context.

    **Analyze the following aspects of the provided image(s):**

    1.  **Overall Mood & Atmosphere:**
        * Describe the general feeling (e.g., minimalist, luxurious, cozy, energetic, futuristic, rustic, playful, sophisticated, calm).
        * Is it bright and airy, dark and moody, dramatic, subdued?

    2.  **Color Palette:**
        * Identify the dominant colors.
        * Identify key accent colors.
        * Describe the color relationships (e.g., monochromatic, analogous, complementary, triadic).
        * Characterize the saturation (vibrant, muted, desaturated).
        * Characterize the brightness/value (light, dark, high contrast, low contrast).

    3.  **Lighting:**
        * Describe the type of lighting (e.g., natural, artificial, studio, ambient).
        * Identify the light direction (e.g., front-lit, side-lit, back-lit, top-down).
        * Describe the quality of light (e.g., hard and sharp, soft and diffused).
        * Characterize the shadows (e.g., deep, soft, minimal, dramatic).
        * Is there a specific lighting effect (e.g., lens flare, bokeh, glow)?

    4.  **Composition & Framing:**
        * Are there strong compositional principles used (e.g., rule of thirds, symmetry, asymmetry, leading lines, golden ratio)?
        * Describe the depth of field (shallow with bokeh, deep focus).
        * Is the framing tight or wide?
        * How is negative space used?
        * What is the typical camera angle or perspective (e.g., eye-level, low angle, high angle)?

    5.  **Textures & Materials:**
        * Describe prominent textures (e.g., smooth, rough, glossy, matte, metallic, wooden, fabric, concrete).
        * Identify any specific materials that define the style.
        * Is the overall feel clean or textured?

    6.  **Key Elements & Motifs (if applicable):**
        * Are there recurring shapes, patterns, objects, or graphic elements that define the style?
        * Is there a particular theme (e.g., nature, technology, urban)?

    7.  **Level of Detail & Complexity:**
        * Is the style detailed and intricate, or simple and clean?
        * Is it photorealistic, illustrative, abstract, painterly?

    **Output Format:**
    Please provide the analysis as a structured style guide, using clear headings or bullet points for each 
    category listed above. Be descriptive and specific.
    Do not add any additional information, but provide the output right away without any introductory text.
    """

COMPARISON_PROMPT = """
    You are an expert image analysis AI. Your task is to meticulously compare the visual style of the provided [IMAGE] against a detailed textual [DESCRIPTION] of an image's style.

    Objective:
    For each distinct stylistic attribute or aspect mentioned in the [DESCRIPTION], you will evaluate how accurately and consistently the [IMAGE] visually embodies that attribute.

    Scoring Guide:
    Assign a numeric score between 0.0 and 1.0 (inclusive) for each point:

    1.0: Perfect, unequivocal match. The image completely and obviously displays this attribute as described.
    0.8 - 0.9: Strong match with minor, negligible deviations or slight ambiguity.
    0.6 - 0.7: Moderate match. The attribute is present but might have noticeable differences, be less prominent, or only partially apply.
    0.3 - 0.5: Weak match. There are some similarities, but significant discrepancies or outright mismatches.
    0.0 - 0.2: No discernible match. The image contradicts the description for this attribute or it is entirely absent.
    Output Format:
    Your output must be a single JSON object.
    Iterate through the [DESCRIPTION] sequentially. Identify each distinct, actionable stylistic statement (each bullet point or sub-bullet point represents a distinct statement).
    Assign a key style_X where X is an incrementing integer starting from 1 for the very first statement and increasing by 1 for each subsequent statement in the [DESCRIPTION]. The value for each key should be the calculated float score.
    The keys are numbered from 1 to seven, so the output keys should alsop be numbered from 1 to 7.
    
    Do NOT include any introductory or concluding text, explanations, or conversational remarks. Output ONLY the JSON object.

    Example of how to number the statements for JSON keys:

    Given this fragment from the description:

    **Analyzing Retail Backgrounds**

    **1. Overall Mood & Atmosphere:**
    *   **General Feeling:** Whimsical, charming, playful, and clean. There's a subtle sophistication balanced with an endearing cuteness.
    *   **Brightness/Atmosphere:** Bright and airy, dominated by the luminous light source in the background, creating an uplifting and optimistic feel.

    **2. Color Palette:**
    *   **Dominant Colors:**
        *   **Background:** Vibrant and lush greens (lime green, emerald green, forest green), creating a natural, leafy forest ambiance.
        *   **Subject:** Dominant greys (various shades from light silver to charcoal) for the chinchilla's fur, pure white for the shirt collar, and light beige/tan for the ground.
    *   **Key Accent Colors:** A strong, saturated red for the bow tie, providing a striking focal point against the greens and greys.
    *   **Color Relationships:** A harmonious blend of analogous greens in the background, contrasted by complementary greys and white in the foreground. The red bow tie acts as a highly effective accent, creating a strong visual pop.
    *   **Saturation:** The greens are moderately to highly saturated, while the red is vivid. The chinchilla's fur exhibits a natural, desaturated grey.
    *   **Brightness/Value:** High contrast, particularly between the bright, almost blown-out light source and the surrounding greens. The foreground subject is well-lit with clear, defined values, creating depth.

    **3. Lighting:**
    *   **Type of Lighting:** Appears to be a stylized form of natural light, mimicking a sunburst or strong overhead sunlight. It could be a composite of natural background lighting and studio-like lighting on the subject.
    *   **Light Direction:** Predominantly back-lit from the upper center, creating a strong glow and subtle halo effect around the chinchilla's head. The subject itself is illuminated by a softer, more diffused front or ambient light, ensuring all details are visible.
    *   **Quality of Light:** The background light is bright, intense, and slightly diffused creating a glow. The light on the subject is soft and smooth, highlighting textures without harsh reflections or shadows.
    *   **Shadows:** Shadows are minimal and soft, primarily providing subtle dimension under the subject and within its fur. There are no harsh or dramatic shadows.
    *   **Specific Lighting Effect:** A prominent sunburst/light ray effect emanating from the top-center in the background.

    **4. Composition & Framing:**
    *   **Compositional Principles:** Strong central framing, placing the main subject (chinchilla) front and center. The overall composition is vertically oriented, emphasizing the height of the subject and background trees.
    *   **Depth of Field:** Shallow depth of field, with the chinchilla in crisp focus and the background heavily blurred (bokeh effect), effectively isolating the subject and drawing immediate attention to it.
    *   **Framing:** A mid-shot/full-body shot of the chinchilla, occupying a significant portion of the vertical frame.
    *   **Negative Space:** The blurred green foliage serves as effective and simple negative space, enhancing the focus on the subject.
    *   **Camera Angle/Perspective:** Eye-level or slightly low-angle perspective, giving the animal a dignified and engaging presence.

    **5. Textures & Materials:**
    *   **Prominent Textures:**
        *   **Subject:** Ultra-soft, fluffy, and dense fur on the chinchilla; smooth, crisp fabric (like cotton or satin) for the white shirt collar and red bow tie.
        *   **Background:** Heavily blurred organic textures suggestive of leaves, foliage, and tree trunks, providing a natural yet indistinct backdrop.
        *   **Ground:** A subtly textured, smooth, light-colored surface (possibly concrete or a paved path).
    *   **Materials:** Fur, polished fabric (bow tie), cotton/linen (shirt collar), natural outdoor elements (trees, leaves), paving/ground material.
    *   **Overall Feel:** Clean and soft in the foreground; organic and blurred in the background.

    **6. Key Elements & Motifs:**
    *   **Recurring elements:** Anthropomorphic animals (specifically small, cute creatures), dressed in formal or semi-formal attire (bow ties, collars), set against lush, natural outdoor environments. The strong, central light source is also a motif.
    *   **Theme:** Whimsical, light-hearted natural elegance with a touch of character.

    **7. Level of Detail & Complexity:**
    *   **Detail:** High level of detail on the primary subject, capturing intricate fur texture and facial features. The background is intentionally simplistic due to heavy blurring.
    *   **Complexity:** Simple and clean composition, typically featuring a single main character. The overall scene is not cluttered.
    *   **Style:** Photorealistic for the animal subject, subtly combined with an almost painterly or illustrative quality for the blurred background and stylized lighting. It appears to be a high-quality digital render or composite image rather than a raw photograph.
    
    The JSON output should look like this:
    
    {"style_1": 0.9, "style_2": 0.8, "style_3": 0.7, "style_4": 0.6, "style_5": 0.5, "style_6": 0.4, "style_7": 0.3}
    
    The keys are numbered from 1 to seven, the floating point numbers are example. You should find fitting values to describe the similarities in the [DESCRIPTION] and the [IMAGE]. 
    Do not include any formatting like markdown or any other text. Just the JSON output.
    """

ERROR_PROMPT = """
    Role: You are an expert Image Quality Assessment AI, specialized in identifying and quantifying malformations in AI-generated images. Your knowledge base includes an exhaustive taxonomy of common generation errors. Your primary directive is to provide a concise, high-signal assessment.

    Objective:

    Analyze the provided image to determine what elements are present (e.g., humans, animals, specific objects, text).
    For each present element, apply the definition of each specific malformation.
    Assign a metric from 0.0 (catastrophic failure) to 1.0 (perfect, no discernible issues) for each applicable malformation type.
    Scoring Guidelines:

    1.0 (Perfect): Absolutely no discernible malformations of this specific type are present.
    0.7 - 0.9 (Minor/Few): Very minor, subtle, or extremely few instances of this malformation. They might be barely noticeable.
    0.4 - 0.6 (Moderate/Visible): Moderate presence of this malformation. Clearly visible, impacts overall quality.
    0.1 - 0.3 (Severe/Many): Severe presence of this malformation. Highly distorted, prevalent, or significantly impacting.
    0.0 (Catastrophic): Complete or near-complete failure in this specific category. Renders the aspect unrecognizable or fundamentally unusable.
    Strict Output Requirements:

    Flat JSON Structure: The output must be a single-level JSON object.
    Key Naming: Each key name must be a concatenation of the full hierarchy path of the malformation, separated by underscores (_).
    Example: anatomical_malformations_hands_fingers_incorrect_finger_count
    Value Only: The value associated with each key must be only the numerical metric (e.g., 0.8), without any details or nested objects.
    Omission of Non-Applicable Elements: If a higher-level category or a specific sub-category for malformations is not applicable to the content of the image (e.g., no animals present, no text to analyze, no objects, or no elements where a specific error type can manifest), then that specific key-value pair must be entirely omitted from the output JSON. Do not include keys for malformations that cannot possibly occur given the image content. For example, if there are no hands, skip all hands_fingers keys. If there's no text, skip all text_symbol_malformations keys.
    Empty Image: If the image is entirely blank or contains no discernible elements to assess, return an empty JSON object {}.

    Flattened Malformation Definitions (Reference List for AI):

    This list defines what each specific malformation represents. Use these definitions to guide your assessment and score assignment.

    anatomical_malformations_hands_fingers_incorrect_finger_count: Too many or too few fingers (e.g., 6, 7, 3, 1).

    anatomical_malformations_hands_fingers_fused_merged_fingers: Fingers appearing stuck together, lacking distinct separation.

    anatomical_malformations_hands_fingers_displaced_misaligned_fingers: Fingers growing from odd places or pointing in unnatural directions.

    anatomical_malformations_hands_fingers_malformed_joints: Fingers bending unnaturally or at impossible angles.

    anatomical_malformations_hands_fingers_incorrect_proportions: Fingers too long/short, too thick/thin.

    anatomical_malformations_hands_fingers_ambiguous_thumbs: Thumbs missing, strangely shaped, or appearing as other fingers.

    anatomical_malformations_hands_fingers_nails: Missing, strangely shaped, or misplaced fingernails.

    anatomical_malformations_hands_fingers_overall_hand_shape_distortion: Hands appearing blob-like, twisted, or unrecognizable.

    anatomical_malformations_hands_fingers_interaction_with_objects: Fingers not gripping objects naturally, merging with objects.

    anatomical_malformations_faces_facial_features_asymmetry: Eyes, nose, mouth, or ears unevenly placed or differing significantly.

    anatomical_malformations_faces_facial_features_mismatched_malformed_features: Eyes without pupils, multiple pupils; mouths with too many/no teeth; noses flattened/distorted; strange ears.

    anatomical_malformations_faces_facial_features_extra_missing_features: Phantom eyes/mouths/noses, or completely missing essential features.

    anatomical_malformations_faces_facial_features_skin_texture_realism: Plastic-like, unnaturally rough, unnatural skin tones, merging with hair/clothing.

    anatomical_malformations_faces_facial_features_expression: Unnatural, forced, blank, or unsettling 'uncanny valley' expressions.

    anatomical_malformations_faces_facial_features_hair: Merging with background, strange textures, floating strands, unnatural partings.

    anatomical_malformations_faces_facial_features_teeth: Too many/few, misaligned, or strangely shaped, often merging into gums.

    anatomical_malformations_bodies_limbs_proportionality_errors: Limbs too long/short, head too large/small for body, torso disproportionate.

    anatomical_malformations_bodies_limbs_joint_malformations: Bending at impossible angles, missing joints, extra joints.

    anatomical_malformations_bodies_limbs_extra_missing_limbs_appendages: Additional or missing arms, legs, or phantom limbs.

    anatomical_malformations_bodies_limbs_merging_blobbing: Limbs merging into torso, other limbs, or background.

    anatomical_malformations_bodies_limbs_unnatural_poses_posture: Contorted, impossible, or extremely rigid poses.

    anatomical_malformations_bodies_limbs_muscle_definition: Over-exaggerated or completely lacking in places.

    anatomical_malformations_bodies_limbs_nudity_clothing_confusion: Clothing melting into skin, or skin appearing where clothing should be.

    anatomical_malformations_animals_creatures_incorrect_limbs_heads: Too many/few legs, tails, heads, or missing body parts.

    anatomical_malformations_animals_creatures_hybridization: Unintentional mixing of different animal features.

    anatomical_malformations_animals_creatures_distorted_anatomy: Twisted bodies, mangled features, or impossible skeletal structures.

    anatomical_malformations_animals_creatures_unnatural_fur_scale_feather_patterns: Disjointed or chaotic textures.

    anatomical_malformations_animals_creatures_facial_malformations: Similar to human faces, but for animals (e.g., misaligned eyes, strange mouths).

    object_prop_malformations_distortion_deformation_melting_liquefaction: Objects appearing to melt or lose solid form.

    object_prop_malformations_distortion_deformation_stretching_squishing: Objects elongated or compressed unnaturally.

    object_prop_malformations_distortion_deformation_bending_warping: Objects appearing to bend or warp without apparent force.

    object_prop_malformations_distortion_deformation_blobbing_amorphousness: Objects losing distinct edges, appearing shapeless.

    object_prop_malformations_distortion_deformation_incorrect_shape_geometric_malformation: Circles as ovals, squares as trapezoids, etc.

    object_prop_malformations_texture_material_inconsistencies_incorrect_material_properties: Metal looking like plastic, wood as stone.

    object_prop_malformations_texture_material_inconsistencies_texture_blurring_fuzziness: Textures lacking detail or appearing smeared.

    object_prop_malformations_texture_material_inconsistencies_repetitive_textures: Repeating patterns where they shouldn't exist.

    object_prop_malformations_texture_material_inconsistencies_material_merging: Different materials bleeding into each other.

    object_prop_malformations_texture_material_inconsistencies_unnatural_reflectivity_gloss: Surfaces too shiny or dull for their material.

    object_prop_malformations_missing_extra_parts_elements: Incomplete objects (car without wheels), spurious random parts.

    object_prop_malformations_compositional_placement_errors_floating_objects: Objects hovering mid-air without support.

    object_prop_malformations_compositional_placement_errors_merging_with_background_other_objects: Objects blending indistinguishably into surroundings.

    object_prop_malformations_compositional_placement_errors_incorrect_scale: Objects too large or too small relative to environment.

    object_prop_malformations_compositional_placement_errors_inconsistent_perspective: Objects appearing at different vanishing points than scene.

    object_prop_malformations_compositional_placement_errors_clipping_interpenetration: Objects passing through each other unrealistically.

    object_prop_malformations_functionality_logical_inconsistencies: Broken/non-functional objects (door without handle), implausible configurations.

    scene_environment_compositional_malformations_perspective_depth_flatness: Lack of depth, making scene appear 2D.

    scene_environment_compositional_malformations_perspective_depth_distorted_perspective: Incorrect or inconsistent vanishing points.

    scene_environment_compositional_malformations_perspective_depth_incorrect_object_placement_in_depth: Foreground objects appearing behind background elements incorrectly.

    scene_environment_compositional_malformations_lighting_shadows_inconsistent_light_sources: Shadows falling in multiple directions where one source should be.

    scene_environment_compositional_malformations_lighting_shadows_missing_shadows: Objects casting no shadows when they should.

    scene_environment_compositional_malformations_lighting_shadows_unnatural_shadows: Shadows too harsh, too soft, or strangely shaped.

    scene_environment_compositional_malformations_lighting_shadows_incorrect_highlights: Highlights where no light source exists or from impossible angles.

    scene_environment_compositional_malformations_lighting_shadows_over_exposure_under_exposure: Parts of image excessively bright or dark, losing detail.

    scene_environment_compositional_malformations_environmental_coherence_impossible_environments: Indoor bleeding into outdoor, conflicting elements (snow in desert).

    scene_environment_compositional_malformations_environmental_coherence_repetitive_patterns: Tiling effects in large areas (walls, terrain).

    scene_environment_compositional_malformations_environmental_coherence_background_blurring_issues: Inconsistent or incorrect background blur.

    scene_environment_compositional_malformations_overall_composition_aesthetics_awkward_cropping: Subjects cut off at odd points, poor framing.

    scene_environment_compositional_malformations_overall_composition_aesthetics_cluttered_chaotic_scenes: Too many elements, lacking clear focal point.

    scene_environment_compositional_malformations_overall_composition_aesthetics_lack_of_artistic_direction: Image appearing generic, uninspired, lacking mood.

    scene_environment_compositional_malformations_overall_composition_aesthetics_stylistic_inconsistency: Elements generated in different artistic styles within image.

    scene_environment_compositional_malformations_overall_composition_aesthetics_color_palette_issues: Unnatural, unbalanced, or clashing colors.

    text_symbol_malformations_garbled_gibberish_text: Unreadable characters, random squiggles, placeholder text.

    text_symbol_malformations_incorrect_language_characters: Attempting English but producing other alphabets.

    text_symbol_malformations_missing_extra_letters: Words misspelled by addition or omission of letters.

    text_symbol_malformations_distorted_text: Text appearing wavy, stretched, melted, or malformed.

    text_symbol_malformations_improper_placement_adherence: Text floating off surfaces, not conforming to 3D objects.

    text_symbol_malformations_symbolic_misinterpretation: Logos, road signs, etc., rendered inaccurately or distorted.

    artifacts_noise_pixelation_low_resolution: Image appears blocky or blurry due to insufficient resolution.

    artifacts_noise_compression_artifacts: Visible blocks or color banding.

    artifacts_noise_digital_noise_grain: Random speckles, static-like interference.

    artifacts_noise_hallucinations_ghosting: Faint, semi-transparent, or random shapes/colors/ghost-like images.

    artifacts_noise_diffusion_artifacts_blurry_fuzzy_patches: Areas lacking detail or appearing smudged.

    artifacts_noise_diffusion_artifacts_over_smoothing: Loss of texture or detail in areas that should have it.

    artifacts_noise_diffusion_artifacts_patchwork_seams: Visible lines or transitions from generated parts.

    artifacts_noise_diffusion_artifacts_color_bleeding: Colors from one area seeping into an adjacent, unrelated area.

    artifacts_noise_diffusion_artifacts_chromatic_aberration: Fringes of color around high-contrast edges.

    semantic_conceptual_errors_misinterpretation_of_prompt: Image deviates significantly from explicit request.

    semantic_conceptual_errors_loss_of_key_prompt_elements: Ignoring crucial details or adjectives within prompt.

    semantic_conceptual_errors_over_under_interpretation: Too literal or too vague generation based on prompt.

    semantic_conceptual_errors_lack_of_desired_mood_emotion: Image's mood contradicts intent.

    semantic_conceptual_errors_inconsistent_narrative_storytelling: Featuring contradictory elements if implied by prompt.

    semantic_conceptual_errors_word_soup_concept_blending: Incoherent blend from multiple conflicting concepts.

    physics_natural_law_violations_gravity_disregard: Objects floating that should be grounded, liquids defying gravity.

    physics_natural_law_violations_material_property_violations: Water looking solid, fire like smoke, opaque glass.

    physics_natural_law_violations_incorrect_reflect_refractions: Reflections where none should be, or geometrically incorrect.

    physics_natural_law_violations_transparency_opacity_errors: Objects that should be transparent are opaque, or vice-versa.

    physics_natural_law_violations_forces_dynamics: Movement or forces depicted unnaturally (e.g., splashes going wrong way).

    Expected Output Format (JSON Example):

    {
    "anatomical_malformations_hands_fingers_incorrect_finger_count": 0.8,
    "anatomical_malformations_hands_fingers_displaced_misaligned_fingers": 0.5,
    "anatomical_malformations_faces_facial_features_asymmetry": 0.9,
    "object_prop_malformations_compositional_placement_errors_floating_objects": 0.6,
    "scene_environment_compositional_malformations_lighting_shadows_missing_shadows": 0.7,
    "text_symbol_malformations_garbled_gibberish_text": 0.2,
    "artifacts_noise_diffusion_artifacts_blurry_fuzzy_patches": 0.4,
    "semantic_conceptual_errors_misinterpretation_of_prompt": 0.3,
    "physics_natural_law_violations_gravity_disregard": 0.1
    // ... only include keys for applicable malformations ...
    }
    
    Image for Analysis:
    """
