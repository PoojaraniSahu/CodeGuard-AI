async function loadAvailableRepos(userId) {
    const container = document.getElementById('available-repos-list');
    container.innerHTML = '<p>Loading...</p>';
    
    try {
        const response = await fetch(`/repos/available?user_id=${userId}`);
        if (!response.ok) throw new Error('Failed to fetch');
        
        const repos = await response.json();
        
        if (repos.length === 0) {
            container.innerHTML = '<p>No repositories found.</p>';
            return;
        }

        container.innerHTML = repos.map(repo => `
            <div class="card repo-card">
                <h3>${repo.full_name}</h3>
                <p class="text-muted">${repo.language || 'Unknown'}</p>
                <button class="btn btn-primary" onclick="connectRepo('${repo.full_name}', ${userId})" style="margin-top: 1rem;">
                    Connect & Add Webhook
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error(error);
        container.innerHTML = `<p style="color: red;">Error loading repositories.</p>`;
    }
}

async function connectRepo(repoName, userId) {
    try {
        const response = await fetch(`/repos/connect?user_id=${userId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repo_name: repoName })
        });
        
        if (response.ok) {
            alert(`Successfully connected ${repoName}!`);
            window.location.reload();
        } else {
            const err = await response.json();
            alert(`Failed to connect: ${err.detail}`);
        }
    } catch (error) {
        console.error(error);
        alert('An error occurred.');
    }
}

async function triggerFullScan(repoId, userId) {
    try {
        const response = await fetch(`/repos/${repoId}/scan?user_id=${userId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            alert('Full repository scan has started! This may take a few minutes depending on the size of the repository. Refresh the page to see results as they come in.');
        } else {
            alert('Failed to start scan.');
        }
    } catch (error) {
        console.error(error);
    }
}
