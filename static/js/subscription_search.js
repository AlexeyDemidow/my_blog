window.addEventListener('load', function() {
    const searchInput = document.getElementById('subscriptions-search-input')
    const resultsBox = document.getElementById('subscriptions-result-box')
    const csrf = getCookie('csrftoken');

    const sendSearchData =(profile_name) => {
        $.ajax({
            type: 'POST',
            url: 'subscriptions_search_result/',
            data: {
                'csrfmiddlewaretoken': csrf,
                'profile_name': profile_name,

            },
            success: (res)=> {
                data = res.data
                if (Array.isArray(data)) {
                    resultsBox.innerHTML = ''
                    data.forEach(profile_name=> {
                        resultsBox.innerHTML += `
                            <div class="catalog">
                                <div class="food_container">
                                    <a href="${profile_name.id}/">
                                        <p><img src="${ profile_name.pic }" style="width: 60px"></p>
                                        <p>${ profile_name.username }</p>
                                        <p>${ profile_name.bio }</p>
                                    </a>
                                </div>
                            </div>`
                    })
                } else {
                    resultsBox.innerHTML = `<b>${data}</b>`
                }
            },
            error: (err)=> {
                console.log(err)
            }
        })
    }

    searchInput.addEventListener('keyup', e=>{
        sendSearchData(e.target.value)
    })

    function getCookie(name) {
          const value = `; ${document.cookie}`;
          const parts = value.split(`; ${name}=`);
          if (parts.length === 2) {
            const csrfToken = parts.pop().split(';').shift();
            return csrfToken;
          }
          return null;
        }
})