$(document).ready(async function () {
    const found = await window.probeApiBase();
    if (!found) {
        alert(
            'Cannot reach the prediction API (ports 5001 / 5000).\n\n' +
                '1) Open: freelance salary predictor\\server\\\n' +
                '2) Double-click run_server.bat\n' +
                '3) Wait until the window shows SERVER_VERSION 3.0.0-FIXED\n' +
                '4) Refresh this page.'
        );
        $('#predict-btn').prop('disabled', true);
        return;
    }
    const API_URL = found.base;
    if (found.health && String(found.health.version || '').indexOf('2.1') === 0) {
        console.warn('Old API detected; run server/run_server.bat for correct experience labels.');
    }

    // 1. Fetch Job Categories to populate Dropdown
    $.get(API_URL + "/get_job_categories", function (data) {
        if (data && data.job_categories) {
            const select = $('#job-category');
            select.empty();
            let html = '<option value="" disabled selected>Select Target Role</option>';
            data.job_categories.forEach(category => {
                // Capitalize properly for the UI
                const displayCat = category.replace(/\w\S*/g, function(txt) {
                    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
                });
                html += `<option value="${category}">${displayCat}</option>`;
            });
            select.append(html);
            
            // Try to load state after categories are populated
            loadState();
        }
    });

    // Form persistence
    function saveState() {
        const state = {
            job_category: $('#job-category').val(),
            experience_level: $('#experience-level').val(),
            job_completed: $('#jobs-completed').val(),
            hourly_rate: $('#hourly-rate').val(),
            project_complexity: $('#project-complexity').val(),
            last_prediction: $('#predicted-salary').text()
        };
        localStorage.setItem('freelance_predictor_state', JSON.stringify(state));
    }

    function loadState() {
        try {
            const saved = localStorage.getItem('freelance_predictor_state');
            if (saved) {
                const state = JSON.parse(saved);
                if (state.job_category) $('#job-category').val(state.job_category);
                if (state.job_completed) $('#jobs-completed').val(state.job_completed);
                if (state.hourly_rate) {
                    $('#hourly-rate').val(state.hourly_rate);
                    if(document.getElementById('rate-display')) {
                        document.getElementById('rate-display').textContent = '$' + state.hourly_rate + '/hr';
                    }
                }
                if (state.experience_level) {
                    $('#experience-level').val(state.experience_level);
                    $('#experience-selector button').each(function() {
                        if ($(this).attr('data-val') === state.experience_level) {
                            // Manually apply active styling without triggering click event loop
                            $('#experience-selector button').removeClass('bg-emerald-950 text-white shadow-md').addClass('bg-slate-100 text-slate-600 hover:bg-black hover:text-white');
                            $(this).removeClass('bg-slate-100 text-slate-600 hover:bg-black hover:text-white').addClass('bg-emerald-950 text-white shadow-md font-bold rounded-lg');
                        }
                    });
                }
                if (state.project_complexity) {
                    $('#project-complexity').val(state.project_complexity);
                    $('#complexity-selector button').each(function() {
                        if ($(this).data('val') == state.project_complexity) {
                            $('#complexity-selector button').removeClass('bg-emerald-950 text-white shadow-md').addClass('bg-slate-100 text-slate-600 hover:bg-slate-200');
                            $(this).removeClass('bg-slate-100 text-slate-600 hover:bg-slate-200').addClass('bg-emerald-950 text-white shadow-md font-bold rounded-lg');
                        }
                    });
                }
                if (state.last_prediction && state.last_prediction !== '--') {
                    $('#predicted-salary').text(state.last_prediction);
                }
            }
        } catch(e) { console.error('Failed to parse local state', e); }
    }

    // Attach listeners to save state automatically on any input change
    $('#prediction-form').on('change input', 'input, select', function() {
        saveState();
    });

    // 2. UI Interactions
    // Experience Level segmented selector
    const expSegs = document.querySelectorAll('#experience-selector button');
    const expInput = document.getElementById('experience-level');
    if (expSegs.length > 0) {
        expSegs.forEach(seg => {
            seg.addEventListener('click', function() {
                expSegs.forEach(s => {
                    s.classList.remove('bg-emerald-950', 'text-white', 'shadow-md');
                    s.classList.add('bg-slate-100', 'text-slate-600', 'hover:bg-black', 'hover:text-white');
                });
                this.classList.remove('bg-slate-100', 'text-slate-600', 'hover:bg-black', 'hover:text-white');
                this.classList.add('bg-emerald-950', 'text-white', 'shadow-md', 'font-bold', 'rounded-lg');
                expInput.value = this.dataset.val;
                saveState();
            });
        });
    }

    const rateSlider = document.getElementById('hourly-rate');
    const rateDisplay = document.getElementById('rate-display');
    if (rateSlider && rateDisplay) {
        rateSlider.addEventListener('input', function() {
            rateDisplay.textContent = '$' + this.value + '/hr';
        });
    }

    // Complexity Buttons
    const segments = document.querySelectorAll('#complexity-selector button');
    const complexityInput = document.getElementById('project-complexity');
    if (segments.length > 0) {
        segments.forEach(segment => {
            segment.addEventListener('click', function(e) {
                e.preventDefault(); // Prevent form submission if they are normal buttons
                
                // Remove active classes
                segments.forEach(s => {
                    s.classList.remove('bg-emerald-950', 'text-white', 'shadow-md');
                    s.classList.add('bg-slate-100', 'text-slate-600', 'hover:bg-slate-200');
                });
                
                // Make clicked active
                this.classList.remove('bg-slate-100', 'text-slate-600', 'hover:bg-slate-200');
                this.classList.add('bg-emerald-950', 'text-white', 'shadow-md', 'font-bold', 'rounded-lg');
                
                complexityInput.value = this.dataset.val;
                saveState();
            });
        });
    }

    // Job Category dynamic subtitle
    $('#job-category').on('change', function() {
        const role = $(this).find('option:selected').text();
        if (role && role !== 'Select Target Role') {
            $('#current-target-role').text(role);
            $('#analysis-subtitle').fadeIn();
        } else {
            $('#analysis-subtitle').hide();
        }
    });

    // New Prediction Reset
    $('#new-prediction-btn').on('click', function() {
        // Clear local storage
        localStorage.removeItem('freelance_predictor_state');
        
        // Redirect to dashboard (index.html) to ensure a guaranteed 'clean slate' refresh
        // This works better than reload() if the user is on insights.html
        window.location.href = 'index.html';
    });

    // 3. Form Submission
    $('#prediction-form').on('submit', function (e) {
        e.preventDefault();

        const btn = $('#predict-btn');
        const originalHtml = btn.html();
        btn.html('<i class="fa-solid fa-spinner fa-spin mr-2"></i> Predicting...');
        btn.prop('disabled', true);

        const jobCategory = $('#job-category').val();
        const experienceLevelVal = $('#experience-level').val();
        const projectComplexityVal = $('#project-complexity').val();

        if(!jobCategory) {
            alert("Please select a Target Role.");
            btn.html(originalHtml);
            btn.prop('disabled', false);
            return;
        }
        
        if(!experienceLevelVal) {
            alert("Please select your Experience Level.");
            btn.html(originalHtml);
            btn.prop('disabled', false);
            return;
        }

        if(!projectComplexityVal) {
            alert("Please select the Project Complexity level.");
            btn.html(originalHtml);
            btn.prop('disabled', false);
            return;
        }

        // Use the visually selected segment — hidden #experience-level can drift after loadState
        const activeExpBtn = document.querySelector('#experience-selector button.bg-primary-container');
        const experienceLevel = activeExpBtn
            ? activeExpBtn.getAttribute('data-val')
            : document.getElementById('experience-level').value;
        if (document.getElementById('experience-level')) {
            document.getElementById('experience-level').value = experienceLevel;
        }

        const payload = {
            job_category: jobCategory,
            experience_level: experienceLevel,
            job_completed: $('#jobs-completed').val(),
            hourly_rate: $('#hourly-rate').val(),
            project_complexity: $('#project-complexity').val()
        };

        $.post(API_URL + "/predict_salary", payload, function (data) {
            btn.html(originalHtml);
            btn.prop('disabled', false);

            if (data && data.estimated_salary !== undefined && data.estimated_salary !== null) {
                const formattedSalary = parseFloat(data.estimated_salary).toLocaleString('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 2
                });
                $('#predicted-salary').text(formattedSalary);
                
                // DYNAMIC FEATURE IMPACT UPDATE
                if (data.feature_importance) {
                    updateFeatureImpact(data.feature_importance);
                }
                
                saveState(); // Save the prediction!
            } else {
                $('#predicted-salary').text("--");
                alert("Failed to predict salary based on inputs.");
            }
        }).fail(function() {
            btn.html(originalHtml);
            btn.prop('disabled', false);
            alert("Failed to connect to the prediction server. Make sure the Flask app is running.");
        });
    });

    // 4. Global Analytics Functions
    window.updateFeatureImpact = function(fi) {
        if (!fi) return;
        
        const mapping = [
            { id: 'experience', key: 'Experience_Level' },
            { id: 'projects',   key: 'Job_Completed' },
            { id: 'rate',       key: 'Hourly_Rate' },
            { id: 'complexity', key: 'Project_Complexity' }
        ];

        mapping.forEach(m => {
            let score = fi[m.key] || 0;
            // Visual scaling to make differences more apparent
            let visualWidth = Math.min(100, score * 1.5);
            
            const bar = $(`#impact-${m.id}-bar`);
            const label = $(`#impact-${m.id}-label`);
            
            if (bar.length) {
                bar.stop().animate({ width: visualWidth + '%' }, 600);
            }
            
            if (label.length) {
                let status = 'Minor';
                if (score > 50) status = 'Critical';
                else if (score > 20) status = 'Strong Impact';
                else if (score > 10) status = 'Moderate';
                label.text(status);
            }
        });
    };

    // Load initial model insights on start
    $.get(API_URL + "/get_model_insights", function(data) {
        if (data.feature_importance) {
            updateFeatureImpact(data.feature_importance);
        }
        if (data.model_r2) {
            $('#model-confidence').text(Math.round(data.model_r2 * 100) + '%');
        }
    });
});

