document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const navbar = document.querySelector('.navbar');
    const navigation = document.querySelector('.navigation');
    
    // Create menu toggle button if it doesn't exist
    let menuToggle = navbar.querySelector('.menu-toggle');
    if (!menuToggle) {
        menuToggle = document.createElement('div');
        menuToggle.className = 'menu-toggle';
        menuToggle.innerHTML = '<span></span><span></span><span></span>';
        
        // Insert menu toggle button before navigation
        if (navigation) {
            navbar.insertBefore(menuToggle, navigation);
        } else {
            navbar.appendChild(menuToggle);
        }
    }
    
    // Create backdrop if it doesn't exist
    let backdrop = document.querySelector('.menu-backdrop');
    if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.className = 'menu-backdrop';
        document.body.appendChild(backdrop);
    }
    
    // Toggle menu functionality
    menuToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        menuToggle.classList.toggle('active');
        navigation.classList.toggle('active');
        backdrop.classList.toggle('active');
        document.body.classList.toggle('overflow-hidden');
    });
    
    // Close menu when backdrop is clicked
    backdrop.addEventListener('click', function() {
        menuToggle.classList.remove('active');
        navigation.classList.remove('active');
        backdrop.classList.remove('active');
        document.body.classList.remove('overflow-hidden');
    });
    
    // Handle dropdown toggles on mobile
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                e.stopPropagation();
                
                this.classList.toggle('active');
                const dropdown = this.nextElementSibling || this.parentElement.querySelector('.dropdown-menu');
                if (dropdown) {
                    dropdown.classList.toggle('show');
                }
            }
        });
    });
    
    // Close dropdowns and mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            // Close mobile menu if clicking outside navigation area
            if (!navigation.contains(e.target) && !menuToggle.contains(e.target)) {
                menuToggle.classList.remove('active');
                navigation.classList.remove('active');
                backdrop.classList.remove('active');
                document.body.classList.remove('overflow-hidden');
            }
        }
    });
    
    // Handle resize events
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            menuToggle.classList.remove('active');
            navigation.classList.remove('active');
            backdrop.classList.remove('active');
            document.body.classList.remove('overflow-hidden');
        }
    });
    
    console.log('Mobile navigation initialized');
});
