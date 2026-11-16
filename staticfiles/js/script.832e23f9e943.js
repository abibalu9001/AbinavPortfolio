
/* ========================================
   HAMBURGER DROPDOWN NAVIGATION
======================================== */

const menuToggle = document.getElementById("menuToggle");
const navLinks = document.getElementById("navLinks");

if (menuToggle && navLinks) {

    // Open and close dropdown
    menuToggle.addEventListener("click", function (event) {
        event.stopPropagation();

        navLinks.classList.toggle("show");
        menuToggle.classList.toggle("active");

        menuToggle.setAttribute(
            "aria-expanded",
            navLinks.classList.contains("show")
        );
    });

    // Close after selecting a page
    navLinks.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", function () {
            navLinks.classList.remove("show");
            menuToggle.classList.remove("active");
            menuToggle.setAttribute("aria-expanded", "false");
        });
    });

    // Close when clicking outside
    document.addEventListener("click", function (event) {
        if (
            !menuToggle.contains(event.target) &&
            !navLinks.contains(event.target)
        ) {
            navLinks.classList.remove("show");
            menuToggle.classList.remove("active");
            menuToggle.setAttribute("aria-expanded", "false");
        }
    });
}


/* ========================================
   HERO TYPING ANIMATION
======================================== */

const typingText = document.getElementById("typing-text");

if (typingText) {

    const roles = [
        "CodeBees Student @CIT",
        "Knight @LeetCode",
        "Machine Learning Enthusiast",
        "Full Stack Developer",
        "Maths Researcher",
        "IoT & Hardware Developer"
    ];

    let roleIndex = 0;
    let charIndex = 0;
    let deleting = false;

    function typeEffect() {

        const currentRole = roles[roleIndex];

        if (!deleting) {

            typingText.textContent =
                currentRole.substring(0, charIndex + 1);

            charIndex++;

            if (charIndex === currentRole.length) {
                deleting = true;
                setTimeout(typeEffect, 1500);
                return;
            }

        } else {

            typingText.textContent =
                currentRole.substring(0, charIndex - 1);

            charIndex--;

            if (charIndex === 0) {
                deleting = false;
                roleIndex = (roleIndex + 1) % roles.length;
            }
        }

        setTimeout(typeEffect, deleting ? 45 : 90);
    }

    typeEffect();
}

document.addEventListener("DOMContentLoaded", function () {

    const countrySelect = document.getElementById("country");
    const stateSelect = document.getElementById("state-region");
    const districtGroup = document.getElementById("district-group");
    const districtSelect = document.getElementById("district");

    if (!countrySelect || !stateSelect || !districtGroup || !districtSelect) {
        return;
    }

    const BASE_URL = "https://countriesnow.space/api/v0.1";
    const INDIA_DATA_URL =
        "https://raw.githubusercontent.com/CodingMation/indian-states-districts/main/data/india_states_districts.min.json";

    let indiaData = null;

    function setOptions(select, placeholder, items) {
        select.innerHTML = "";

        const first = document.createElement("option");
        first.value = "";
        first.textContent = placeholder;
        select.appendChild(first);

        items.forEach(item => {
            const option = document.createElement("option");
            option.value = item.value;
            option.textContent = item.label;

            if (item.code) {
                option.dataset.code = item.code;
            }

            select.appendChild(option);
        });
    }

    function setLoading(select, message) {
        select.innerHTML = `<option value="">${message}</option>`;
        select.disabled = true;
    }

    function resetDistrict() {
        districtGroup.hidden = true;
        districtSelect.required = false;
        setLoading(districtSelect, "Choose a state first");
    }

    // Load India dataset once.
    async function getIndiaData() {
        if (indiaData) return indiaData;

        const response = await fetch(INDIA_DATA_URL);

        if (!response.ok) {
            throw new Error("Unable to load India location data");
        }

        indiaData = await response.json();
        return indiaData;
    }

    // Load all countries.
    async function loadCountries() {
        setLoading(countrySelect, "Loading countries...");

        try {
            const response = await fetch(`${BASE_URL}/countries/iso`);

            if (!response.ok) throw new Error("Country API failed");

            const result = await response.json();

            if (result.error || !Array.isArray(result.data)) {
                throw new Error(result.msg || "Invalid country data");
            }

            const countries = result.data
                .map(item => ({
                    value: item.name || item.country,
                    label: item.name || item.country
                }))
                .filter(item => item.value)
                .sort((a, b) => a.label.localeCompare(b.label));

            setOptions(countrySelect, "Select your country", countries);
            countrySelect.disabled = false;

        } catch (error) {
            setLoading(countrySelect, "Unable to load countries");
            console.error(error);
        }
    }

    // Load worldwide states and provinces.
    async function loadGlobalStates(country) {
        setLoading(stateSelect, "Loading states / regions...");

        try {
            const response = await fetch(`${BASE_URL}/countries/states`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ country: country })
            });

            if (!response.ok) throw new Error("State API failed");

            const result = await response.json();

            if (result.error) {
                throw new Error(result.msg || "State data unavailable");
            }

            const states = result.data?.states || [];

            if (!states.length) {
                setOptions(stateSelect, "No regions available", []);
                stateSelect.disabled = true;
                return;
            }

            const items = states.map(state => ({
                value: typeof state === "string" ? state : state.name,
                label: typeof state === "string" ? state : state.name
            }));

            setOptions(stateSelect, "Select your state / region", items);
            stateSelect.disabled = false;

        } catch (error) {
            setLoading(stateSelect, "Unable to load states / regions");
            console.error("State API error:", error);
        }
    }

    // Load Indian states from the India dataset.
    async function loadIndianStates() {
        setLoading(stateSelect, "Loading Indian states...");

        try {
            const data = await getIndiaData();

            // Expected dataset structure: array of state objects.
            const states = Array.isArray(data)
                ? data
                : data.states || data.data || [];

            const items = states.map(state => ({
                value: state.name,
                label: state.name,
                code: state.code
            })).filter(state => state.value);

            if (!items.length) {
                throw new Error("Unexpected India dataset structure");
            }

            setOptions(stateSelect, "Select your state / UT", items);
            stateSelect.disabled = false;

        } catch (error) {
            setLoading(stateSelect, "Unable to load Indian states");
            console.error("India states error:", error);
        }
    }

    // Load Indian districts.
    async function loadIndianDistricts(stateCode, stateName) {
        setLoading(districtSelect, "Loading districts...");

        try {
            const data = await getIndiaData();

            const states = Array.isArray(data)
                ? data
                : data.states || data.data || [];

            const selectedState = states.find(state =>
                state.code === stateCode ||
                state.name.toLowerCase() === stateName.toLowerCase()
            );

            if (!selectedState) {
                throw new Error("Selected state not found in dataset");
            }

            const districts = selectedState.districts || [];

            const items = districts.map(district => ({
                value: typeof district === "string" ? district : district.name,
                label: typeof district === "string" ? district : district.name
            })).filter(item => item.value);

            setOptions(districtSelect, "Select your district", items);
            districtSelect.disabled = items.length === 0;

        } catch (error) {
            setLoading(districtSelect, "Unable to load districts");
            console.error("District loading error:", error);
        }
    }

    // Country change.
    countrySelect.addEventListener("change", async function () {

        const country = this.value;

        setLoading(stateSelect, "Loading states / regions...");
        resetDistrict();

        if (!country) return;

        if (country.toLowerCase() === "india") {
            await loadIndianStates();
        } else {
            await loadGlobalStates(country);
        }
    });

    // State change.
    stateSelect.addEventListener("change", async function () {

        const country = countrySelect.value;
        const selectedOption = this.options[this.selectedIndex];

        resetDistrict();

        if (country.toLowerCase() !== "india" || !selectedOption.value) {
            return;
        }

        districtGroup.hidden = false;
        districtSelect.required = true;

        await loadIndianDistricts(
            selectedOption.dataset.code,
            selectedOption.value
        );
    });

    loadCountries();

});

/* =========================================
   UNIVERSAL SEQUENTIAL PAGE REVEAL
   Applies to every portfolio page
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        return;
    }

    const page = document.querySelector(
        "main, .main-content, .page-content, body"
    );

    if (!page) return;

    const sections = page.querySelectorAll(
        ".page-section, main > section, body > section"
    );

    let delay = 0.15;

    function reveal(element) {
        if (
            element.classList.contains("page-reveal") ||
            element.closest("header, nav, footer") ||
            element.closest(".menu-dropdown")
        ) {
            return;
        }

        element.classList.add("page-reveal");
        element.style.animationDelay = `${delay}s`;
        delay += 0.12;
    }

    sections.forEach(section => {

        // Reveal section heading elements individually
        const heading = section.querySelector(".section-heading");

        if (heading) {
            [...heading.children].forEach(reveal);
        }

        // Reveal direct content blocks
        [...section.children].forEach(child => {

            if (child === heading) return;

            const children = [...child.children];

            const isCardContainer =
                children.length > 1 &&
                (
                    getComputedStyle(child).display === "grid" ||
                    getComputedStyle(child).display === "flex"
                );

            if (isCardContainer) {
                children.forEach(reveal);
            } else {
                reveal(child);
            }
        });
    });

    // Handle pages with content outside .page-section
    if (sections.length === 0) {
        [...page.children].forEach(reveal);
    }

});
