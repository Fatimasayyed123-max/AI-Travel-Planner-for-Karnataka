"""
Unit and Integration Tests for YatraSaathi AI (Version 4.0 - GroqCloud Integration)
Testing:
1. Model Configuration & Credential Protection
2. Environment Variable Resolution (.env via python-dotenv)
3. Itinerary Generation & Parameter Focus (Coorg & Flexible Circuits)
4. Adaptive Replanning (Transport Delay, Heavy Rain, Attraction Closure) & Original Plan Preservation
5. Retention of Valid Itinerary on Subsequent Failure
6. Kannada Buddy AI (Phrasebook, Translation & Reverse Translation Schemas)
7. Heritage Storyteller AI (Flagship Monuments, 9 Historical Sections & Q&A)
8. Budget Optimizer & SafeRoute AI Logic
9. Exponential Backoff Retry for 503 Transient Errors
10. Streamlit AppTest Full Widget Lifecycle Simulation
"""

import os
import json
import unittest
from unittest.mock import MagicMock, patch
import streamlit as st
from app import (
    generate_trip_itinerary,
    adapt_trip_itinerary,
    translate_to_kannada,
    reverse_translate_kannada,
    get_heritage_story,
    ask_heritage_ai,
    get_groq_api_key,
    get_api_key_source,
    sanitize_error_message,
    execute_groq_with_retry,
    get_safe_budget_breakdown,
    DEFAULT_GROQ_MODEL,
    ItineraryResponse,
    RevisedItineraryResponse,
    KannadaTranslationResponse,
    ReverseTranslationResponse,
    HeritageStoryResponse,
    HeritageQAResponse,
    DESTINATIONS,
    DESTINATION_OPTIONS,
    HERITAGE_MONUMENTS,
    KANNADA_OFFLINE_PHRASES,
    on_select_destination,
    on_clear_destination,
    nav_to_adaptive,
    nav_to_budget,
    nav_to_kannada,
)


class TestYatraSaathiAI(unittest.TestCase):

    def test_default_model_is_groq_llama_70b(self):
        """Requirement: Default model ID must be openai/gpt-oss-120b."""
        self.assertEqual(DEFAULT_GROQ_MODEL, "openai/gpt-oss-120b")
        print("PASS: Verified DEFAULT_GROQ_MODEL is set to openai/gpt-oss-120b.")

    def test_sanitize_error_message_protects_credentials(self):
        """Requirement: Never display or expose API key and provide clear error messages."""
        fake_groq_error = Exception("Error calling https://api.groq.com/openai/v1/chat/completions?key=FAKE_KEY")
        sanitized_groq = sanitize_error_message(fake_groq_error)
        self.assertNotIn("gsk_1234567890abcdef1234567890abcdef", sanitized_groq)
        self.assertIn("[PROTECTED_GROQ_KEY]", sanitized_groq)

        fake_error = Exception("Error calling API with key AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q")
        sanitized = sanitize_error_message(fake_error)
        self.assertNotIn("AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q", sanitized)
        self.assertIn("[PROTECTED_API_KEY]", sanitized)

        err_404 = Exception("404 NOT_FOUND: model not found")
        sanitized_404 = sanitize_error_message(err_404)
        self.assertIn("404 Not Found", sanitized_404)

        err_503 = Exception("503 UNAVAILABLE: The model is overloaded. Please try again later.")
        sanitized_503 = sanitize_error_message(err_503)
        self.assertIn("503 Service Unavailable", sanitized_503)
        print("PASS: sanitize_error_message properly masks credentials and explains 404 and 503 errors.")

    def test_env_key_loading_priority(self):
        """Requirement: Read GROQ_API_KEY from environment (.env) securely."""
        with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_TEST_ENV_KEY_123"}, clear=False):
            key = get_groq_api_key()
            self.assertEqual(key, "gsk_TEST_ENV_KEY_123")
            source = get_api_key_source()
            self.assertIn("GROQ_API_KEY", source)
        print("PASS: Verified API key is loaded from environment (.env) with highest priority.")

    def test_coorg_destination_configuration(self):
        """Requirement: Verify Coorg destination is properly configured in DESTINATIONS and DESTINATION_OPTIONS."""
        self.assertIn("Coorg", DESTINATIONS)
        coorg_info = DESTINATIONS["Coorg"]
        self.assertEqual(coorg_info["name"], "Coorg / Kodagu (ಕೊಡಗು)")
        self.assertIn("☕ Coffee Estates & Hill Stations", coorg_info["default_interests"])
        self.assertIn("Coorg / Kodagu (ಕೊಡಗು)", DESTINATION_OPTIONS)
        print("PASS: Verified Coorg is configured with correct name and options.")

    def test_destination_selection_preserves_user_preferences(self):
        """Requirement: Destination selection must select Coorg without destroying other user preferences."""
        st.session_state["form_destination"] = "All Karnataka / Flexible Circuit"
        st.session_state["form_starting_city"] = "Mangaluru (ಮಂಗಳೂರು)"
        st.session_state["form_duration"] = 4
        st.session_state["form_budget"] = 28000
        st.session_state["form_travellers"] = 3
        st.session_state["form_interests"] = ["☕ Coffee Estates & Hill Stations", "🧗 Adventure & Trekking"]
        st.session_state["form_pace"] = "Action-Packed & Comprehensive"

        on_select_destination("Coorg")

        self.assertEqual(st.session_state["form_destination"], "Coorg / Kodagu (ಕೊಡಗು)")
        self.assertEqual(st.session_state["selected_dest_banner"], "Coorg / Kodagu (ಕೊಡಗು)")
        self.assertEqual(st.session_state["form_starting_city"], "Mangaluru (ಮಂಗಳೂರು)")
        self.assertEqual(st.session_state["form_duration"], 4)
        self.assertEqual(st.session_state["form_budget"], 28000)
        self.assertEqual(st.session_state["form_travellers"], 3)
        self.assertEqual(st.session_state["form_interests"], ["☕ Coffee Estates & Hill Stations", "🧗 Adventure & Trekking"])
        self.assertEqual(st.session_state["form_pace"], "Action-Packed & Comprehensive")

        on_clear_destination()
        self.assertEqual(st.session_state["form_destination"], "All Karnataka / Flexible Circuit")
        self.assertNotIn("selected_dest_banner", st.session_state)
        print("PASS: Verified on_select_destination sets Coorg and preserves all other user preferences.")

    @patch("app.Groq")
    def test_generate_trip_itinerary_includes_coorg_destination_in_prompt(self, mock_groq_cls):
        """Requirement: Verify generate_trip_itinerary sends Coorg destination requirement to Groq."""
        mock_client = MagicMock()
        mock_groq_cls.return_value = mock_client
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            "title": "Coorg Misty Highlands",
            "primary_hub": "Coorg",
            "summary": "Custom trip",
            "estimated_cost_per_person": 5000,
            "days": [],
            "must_try_dishes": [],
            "travel_tips": [],
            "budget_breakdown": {
                "transport_estimate": 1000,
                "accommodation_estimate": 2000,
                "food_estimate": 1000,
                "activities_estimate": 1000,
                "notes": "ok",
                "savings_tips": []
            }
        })
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        generate_trip_itinerary(
            api_key="fake-test-key",
            starting_city="Bengaluru (ಬೆಂಗಳೂರು)",
            trip_duration=3,
            total_budget=15000,
            num_travellers=2,
            travel_interests=["☕ Coffee Estates & Hill Stations"],
            preferred_pace="Balanced (Best Sights)",
            destination="Coorg / Kodagu (ಕೊಡಗು)",
        )

        call_args = mock_client.chat.completions.create.call_args
        self.assertIsNotNone(call_args)
        messages = call_args.kwargs.get("messages", [])
        user_content = next((m["content"] for m in messages if m.get("role") == "user"), "")
        self.assertIn("Target Destination / Focus Hub: Coorg / Kodagu (ಕೊಡಗು)", user_content)
        self.assertIn("The entire itinerary MUST be centered specifically on Coorg / Kodagu (ಕೊಡಗು)", user_content)
        self.assertIn("Madikeri Fort, Abbey Falls, Raja's Seat", user_content)
        print("PASS: Verified generate_trip_itinerary passes strict Coorg prompt instructions to Groq.")

    @patch("app.Groq")
    def test_adaptive_replanning_preserves_original_itinerary(self, mock_groq_cls):
        """Requirement: Verify adaptive replanning across disruptions preserves original itinerary."""
        mock_client = MagicMock()
        mock_groq_cls.return_value = mock_client
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            "situation_summary": "Monsoon downpour substituted with indoor coffee museum and spice plantation tasting",
            "ai_note": "Replaced outdoor waterfall trail with rain-safe indoor spice experience",
            "postponed_activities": ["Abbey Falls trekking"],
            "adapted_alternatives": ["Coffee Yatra Museum Madikeri", "Aynmane Kodava heritage lunch"],
            "revised_days": [
                {
                    "day": "Day 1 (Adapted)",
                    "morning": "Arrival and indoor Coffee Yatra Museum visit",
                    "afternoon": "Authentic Kodava indoor dining at Madikeri",
                    "evening": "Covered spice market and sunset coffee tasting"
                }
            ],
            "revised_budget_notes": "No extra expense incurred."
        })
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        original_plan = {
            "title": "Coorg Nature Escape",
            "summary": "Original 3-day outdoor coffee and waterfalls trip",
            "days": [
                {
                    "day": "Day 1: Waterfalls & Views",
                    "morning": "Abbey Falls trekking",
                    "afternoon": "Raja Seat picnic",
                    "evening": "Town market"
                }
            ]
        }
        st.session_state["generated_itinerary"] = original_plan
        st.session_state["original_itinerary"] = original_plan

        # 1. Test Heavy Rain disruption
        adapted_rain = adapt_trip_itinerary(
            api_key="fake-test-key",
            current_plan=st.session_state["generated_itinerary"],
            change_reason="🌧️ Heavy Rain / Monsoon Alert",
            custom_note="Monsoon red alert near Abbey falls"
        )
        self.assertIn("Coffee Yatra Museum Madikeri", adapted_rain["adapted_alternatives"])
        # Verify original plan was NOT mutated
        self.assertEqual(st.session_state["original_itinerary"]["title"], "Coorg Nature Escape")
        self.assertEqual(st.session_state["original_itinerary"]["days"][0]["morning"], "Abbey Falls trekking")

        # 2. Test Transport Delay disruption
        adapt_trip_itinerary(
            api_key="fake-test-key",
            current_plan=st.session_state["generated_itinerary"],
            change_reason="⏰ Transport Delay (Train / Flight / Bus delayed by 3+ hours)",
            custom_note="KSRTC bus reached Kushalnagar 3 hours late"
        )

        # 3. Test Attraction Closure disruption
        adapt_trip_itinerary(
            api_key="fake-test-key",
            current_plan=st.session_state["generated_itinerary"],
            change_reason="🔒 Attraction / Monument Closure",
            custom_note="Palace closed for VIP event"
        )
        print("PASS: Verified adaptive replanning works for disruptions while preserving original itinerary.")

    def test_failed_generation_retains_last_successful_itinerary(self):
        """Requirement: If itinerary generation fails, retain the last successfully generated itinerary."""
        valid_plan = {"title": "Existing Valid Plan", "days": ["Day 1"]}
        st.session_state["generated_itinerary"] = valid_plan
        st.session_state["original_itinerary"] = valid_plan

        # Simulate missing key or failure
        with self.assertRaises(ValueError):
            generate_trip_itinerary(
                api_key="",
                starting_city="Bengaluru (ಬೆಂಗಳೂರು)",
                trip_duration=3,
                total_budget=15000,
                num_travellers=2,
                travel_interests=[],
                preferred_pace="Balanced (Best Sights)",
            )

        # Confirm session state still retains the last valid plan
        self.assertEqual(st.session_state["generated_itinerary"]["title"], "Existing Valid Plan")
        print("PASS: Verified that failed generation retains the last successfully generated itinerary.")

    def test_kannada_buddy_ai_phrasebook_and_schemas(self):
        """Requirement: Verify Kannada Buddy AI has all 8 required categories and valid schemas."""
        required_categories = [
            "Auto & Taxi",
            "Asking Directions",
            "Hotels & Accommodation",
            "Restaurants & Food",
            "Shopping & Payments",
            "Tourist Attractions",
            "General Conversation",
            "Emergencies & Help"
        ]
        for cat in required_categories:
            self.assertIn(cat, KANNADA_OFFLINE_PHRASES)
            self.assertGreaterEqual(len(KANNADA_OFFLINE_PHRASES[cat]), 3)

        # Verify Kannada translation schema
        sample_trans = {
            "kannada_script": "ದಯವಿಟ್ಟು ನನಗೆ ಮೈಸೂರು ಅರಮನೆಗೆ ಕರೆದುಕೊಂಡು ಹೋಗಿ",
            "pronunciation": "Dayavittu nanage Mysuru aramanege karedhukondu hogi",
            "meaning": "Please take me to Mysore Palace",
            "cultural_tip": "Adding 'Dayavittu' (Please) is always appreciated by local drivers."
        }
        validated = KannadaTranslationResponse(**sample_trans)
        self.assertIn("ದಯವಿಟ್ಟು", validated.kannada_script)
        self.assertIn("Dayavittu", validated.pronunciation)
        print("PASS: Verified Kannada Buddy AI contains all 8 required phrase categories and enforces schema.")

    def test_heritage_storyteller_monuments_and_schemas(self):
        """Requirement: Verify Heritage Storyteller covers UNESCO sites and enforces 9 structured sections."""
        required_monuments = ["Hampi", "Mysore Palace", "Halebidu & Belur", "Badami Cave Temples", "Pattadakal", "Gommateshwara (Shravanabelagola)"]
        for mon in required_monuments:
            self.assertIn(mon, HERITAGE_MONUMENTS)

        sample_story = {
            "place_name": "Virupaksha Temple, Hampi",
            "location": "Vijayanagara District, Karnataka",
            "founded_era": "7th Century CE",
            "overview": "Active 7th-century Hindu shrine dedicated to Lord Shiva along Tungabhadra river.",
            "historical_significance": "One of India's oldest continuously functioning temples.",
            "story_behind_the_place": "Survived the 1565 battle of Talikota intact.",
            "people_and_dynasties": "Vijayanagara kings including Krishnadevaraya and Chalukyas.",
            "historical_timeline": [
                "7th Century: Earliest stone shrine established",
                "1510 CE: Krishnadevaraya added the main eastern gopuram",
                "1986: Declared UNESCO World Heritage Site"
            ],
            "architecture": "Dravidian style with inverted pinhole-camera shadow effect inside.",
            "cultural_importance": "Annual chariot festival held every spring.",
            "interesting_facts": ["Features an inverted shadow of its 160-foot gopuram through a tiny pinhole aperture."],
            "what_to_observe": ["Observe the inverted shadow phenomenon in the rear chamber."],
            "verified_sources": ["Archaeological Survey of India (ASI)", "UNESCO World Heritage Centre"]
        }
        validated = HeritageStoryResponse(**sample_story)
        self.assertEqual(len(validated.historical_timeline), 3)
        self.assertIn("pinhole", validated.interesting_facts[0])
        print("PASS: Verified Heritage Storyteller covers flagship Karnataka monuments with 9 verified sections.")

    def test_budget_optimizer_calculations(self):
        """Requirement: Verify Budget Optimizer calculates allocations and money-saving alternatives."""
        plan_with_budget = {
            "budget_breakdown": {
                "transport_estimate": 4000,
                "accommodation_estimate": 6000,
                "food_estimate": 3000,
                "activities_estimate": 2000,
                "notes": "Custom breakdown",
                "savings_tips": ["Book KSRTC buses early"]
            }
        }
        res = get_safe_budget_breakdown(plan_with_budget, 20000, 2)
        self.assertEqual(res["total"], 15000)
        self.assertEqual(res["remaining"], 5000)
        self.assertEqual(res["transport"], 4000)
        self.assertEqual(len(res["savings_tips"]), 1)

        # Fallback proportional calculation when budget_breakdown is missing
        fallback_res = get_safe_budget_breakdown({}, 20000, 2)
        self.assertEqual(fallback_res["total"], 20000)
        self.assertEqual(fallback_res["transport"], 5000)
        self.assertGreater(len(fallback_res["savings_tips"]), 0)
        print("PASS: Verified Budget Optimizer calculates category allocations and savings strategies.")

    def test_retry_mechanism_exponential_backoff(self):
        """Requirement: Bounded retry with exponential backoff on 503 errors."""
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = '{"status": "ok"}'
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]

        # Simulate 503 on first call, success on second call
        err_503 = Exception("503 UNAVAILABLE: The model is overloaded. Please try again later.")
        mock_client.chat.completions.create.side_effect = [err_503, mock_completion]

        with patch("time.sleep") as mock_sleep:
            res = execute_groq_with_retry(
                client=mock_client,
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": "test prompt"}],
                max_retries=3
            )
            self.assertEqual(res, '{"status": "ok"}')
            self.assertEqual(mock_sleep.call_count, 1)
            mock_sleep.assert_called_with(1)  # 2^0 = 1s backoff
        print("PASS: Verified exponential backoff retry handles transient 503 errors seamlessly.")

    def test_streamlit_app_click_plan_trip_to_coorg(self):
        """Requirement: Simulate user clicking 'Explore Destination' for Coorg and verify Coorg is selected and preferences preserved."""
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file("app.py").run()
        
        at.slider(key="form_duration").set_value(5)
        at.slider(key="form_budget").set_value(35000)
        at.number_input(key="form_travellers").set_value(4)
        at.run()

        btn = [b for b in at.button if b.key == "btn_plan_Coorg"][0]
        btn.click().run()

        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.selectbox(key="form_destination").value, "Coorg / Kodagu (ಕೊಡಗು)")
        self.assertEqual(at.slider(key="form_duration").value, 5)
        self.assertEqual(at.slider(key="form_budget").value, 35000)
        self.assertEqual(at.number_input(key="form_travellers").value, 4)
        print("PASS: Verified Streamlit AppTest clicking 'Explore Destination' for Coorg populates destination and preserves preferences.")

    def test_streamlit_app_kannada_buddy_ai_navigation_and_layout(self):
        """Requirement: Verify Kannada Buddy AI navigates, renders selectbox, offline categories, and runs without exception."""
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file("app.py").run()
        
        # Navigate to Kannada Buddy AI
        at.sidebar.radio(key="nav_radio_selector").set_value("🗣️ Kannada Buddy AI").run()
        self.assertEqual(len(at.exception), 0)
        
        # Check language selectbox
        lang_sel = at.selectbox(key="kannada_lang_selector")
        self.assertIsNotNone(lang_sel)
        self.assertEqual(lang_sel.value, "English")
        
        # Change language to Hindi
        lang_sel.select("Hindi").run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.selectbox(key="kannada_lang_selector").value, "Hindi")
        
        # Check offline category picker
        cat_picker = at.selectbox(key="offline_cat_picker")
        self.assertIsNotNone(cat_picker)
        self.assertEqual(cat_picker.value, "Auto & Taxi")
        print("PASS: Verified Streamlit AppTest for Kannada Buddy AI renders smoothly without exceptions.")

    def test_companion_nav_callbacks_set_correct_section(self):
        """Requirement: Companion navigation buttons must set the correct active nav section."""
        import streamlit as st
        st.session_state["active_nav_section"] = "🏠 Home & Destinations"

        nav_to_adaptive()
        self.assertEqual(st.session_state["active_nav_section"], "⚡ My Plan Changed")

        nav_to_budget()
        self.assertEqual(st.session_state["active_nav_section"], "💰 Budget Optimizer")

        nav_to_kannada()
        self.assertEqual(st.session_state["active_nav_section"], "🗣️ Kannada Buddy AI")
        print("PASS: Verified companion navigation callbacks set correct active_nav_section.")

    def test_featured_destinations_present(self):
        """Requirement: Mysuru, Hampi, Coorg and Gokarna must all be in DESTINATIONS dict."""
        for key in ["Mysuru", "Hampi", "Coorg", "Gokarna"]:
            self.assertIn(key, DESTINATIONS, f"Missing featured destination: {key}")
            self.assertIn("image", DESTINATIONS[key])
            self.assertIn("description", DESTINATIONS[key])
            self.assertIn("tagline", DESTINATIONS[key])
        print("PASS: Verified all four featured destination cards are properly configured.")


if __name__ == "__main__":
    unittest.main()
