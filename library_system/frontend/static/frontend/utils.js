const identityProviderUrl = 'http://localhost:8000';
const gatewayUrl = 'http://localhost:8080';

function setCookie(name, value, days) {
  var expires = "";
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function checkCookie(cookieName) {
  return document.cookie.split(';').some(function (item) {
    return item.trim().startsWith(cookieName + '=');
  });
}

function deleteCookie(name) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function getCookie(name) {
  const cookies = document.cookie.split('; ');
  for (const cookie of cookies) {
    const [cookieName, cookieValue] = cookie.split('=');
    if (cookieName === name) {
      return cookieValue;
    }
  }
  return null;
}

async function validateToken(token) {
  const url = new URL('/api/v1/validate', identityProviderUrl);
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ id_token: token }),
  });
  return response.json();
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function generateTodayDate() {
  const today = new Date();
  return formatDate(today);
}

function generateDateOneMonthFromNow() {
  const today = new Date();
  const oneMonthFromNow = new Date(today.getFullYear(), today.getMonth() + 1, today.getDate());
  return formatDate(oneMonthFromNow);
}

function dynamicBooks(books, document, bookContainer, idToken, username) {
  books.forEach(book => {
    const bookBox = document.createElement("div");
    bookBox.className = "book-box";

    const bookInfo = document.createElement("div");
    bookInfo.className = "book-info";

    const bookTitle = document.createElement("h3");
    bookTitle.className = "book-title";
    bookTitle.textContent = book.book.name;

    const bookAuthor = document.createElement("p");
    bookAuthor.className = "book-author";
    bookAuthor.textContent = book.book.author;

    const bookGenre = document.createElement("p");
    bookGenre.className = "book-genre";
    bookGenre.textContent = book.book.genre;

    const libraryName = document.createElement("p");
    libraryName.className = "library-name";
    libraryName.textContent = book.library.name;

    const libraryAddress = document.createElement("p");
    libraryAddress.className = "library-address";
    libraryAddress.textContent = book.library.address + ", " + book.library.city;

    bookInfo.appendChild(bookTitle);
    bookInfo.appendChild(bookAuthor);
    bookInfo.appendChild(bookGenre);
    bookInfo.appendChild(libraryName);
    bookInfo.appendChild(libraryAddress);

    const bookStatus = document.createElement("div");
    bookStatus.className = "book-status";

    const statusValue = document.createElement("p");
    statusValue.className = "status-value-" + book.status;
    statusValue.textContent = book.status;

    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric', timeZoneName: 'short' };
    const startDate = document.createElement("p");
    startDate.className = "date-value";
    const sDate = new Date(book.startDate)
    startDate.textContent = "Start Date: " + sDate.toDateString('en-US', options);

    const tillDate = document.createElement("p");
    tillDate.className = "date-value";
    const tDate = new Date(book.tillDate)
    tillDate.textContent = "Till Date: " + tDate.toDateString('en-US', options);

    // DIALOG

    const returnDialog = document.createElement("dialog");
    returnDialog.id = "return-dialog";

    const dialogBookTitle = document.createElement("p");
    dialogBookTitle.className = "book-title";

    const dialogBookAuthor = document.createElement("p");

    const labelBookCondition = document.createElement("label");
    labelBookCondition.textContent = "Book condition ";
    labelBookCondition.setAttribute("for", "book-condition");

    const selectBookCondition = document.createElement("select");
    selectBookCondition.className = "condition-select";

    const conditions = ["EXCELLENT", "GOOD", "BAD"];
    for (const condition of conditions) {
      const option = document.createElement("option");
      option.value = condition;
      option.textContent = condition.charAt(0) + condition.slice(1).toLowerCase();
      selectBookCondition.appendChild(option);
    }

    const lineBreak = document.createElement("br");

    const dialogReturnButton = document.createElement("button");
    dialogReturnButton.id = "return-button";
    dialogReturnButton.className = "rent-button";
    dialogReturnButton.textContent = "Return";

    const cancelButton = document.createElement("button");
    cancelButton.id = "cancel-button";
    cancelButton.className = "cancel-button";
    cancelButton.textContent = "Cancel";

    returnDialog.appendChild(dialogBookTitle);
    returnDialog.appendChild(dialogBookAuthor);
    returnDialog.appendChild(labelBookCondition);
    returnDialog.appendChild(selectBookCondition);
    returnDialog.appendChild(lineBreak);
    returnDialog.appendChild(dialogReturnButton);
    returnDialog.appendChild(cancelButton);

    const returnResultDialog = document.getElementById("return-result-dialog");
    const returnResultMsg = document.getElementById("return-result");
    const closeButton = document.getElementById("close-button");

    dialogReturnButton.addEventListener("click", () => {
      returnDialog.close();
      returnResultDialog.showModal();
      const condition = selectBookCondition.value;
      returnBook(idToken, username, book.reservationUid, condition)
        .then(response => {
          if (response.status === 204) {
            returnResultMsg.textContent = "Successfuly returned the book!";
          } else {
            returnResultMsg.textContent = "Unable to return this book.";
          }
        })
        .catch(error => {
          console.log(error);
          returnResultMsg.textContent = "Unable to return this book.";
        });
    });
    cancelButton.addEventListener("click", () => {
      returnDialog.close();
    });
    closeButton.addEventListener("click", () => {
      returnResultDialog.close();
      location.reload();
    });

    bookStatus.appendChild(statusValue);
    bookStatus.appendChild(startDate);
    bookStatus.appendChild(tillDate);

    if (book.status === "RENTED") {
      const returnButton = document.createElement("button");
      returnButton.className = "return-button";
      returnButton.textContent = "Return";

      returnButton.addEventListener("click", () => {
        console.log("Return button clicked for:", book.book.name);
        dialogBookTitle.textContent = book.book.name;
        dialogBookAuthor.textContent = "by " + book.book.author;
        returnDialog.showModal();
      });
      
      bookStatus.appendChild(returnButton);
    }

    bookBox.appendChild(bookInfo);
    bookBox.appendChild(bookStatus);

    bookContainer.appendChild(bookBox);
    bookContainer.appendChild(returnDialog);
  });
}

function dynamicLibraries(libraries, document, libraryContainer, booksUrl) {
  for (let i = 0; i < libraries.length; i++) {
    const library = libraries[i];
    console.log(library);

    const libraryBox = document.createElement("div");
    libraryBox.className = "library-box";

    const libraryInfo = document.createElement("div");
    libraryInfo.className = "library-info";

    const libraryName = document.createElement("p");
    libraryName.className = "library-name";
    libraryName.textContent = (i + 1) + ". " + library.name;

    const libraryAddress = document.createElement("p");
    libraryAddress.className = "library-address";
    libraryAddress.textContent = library.address + ", " + library.city;

    libraryInfo.appendChild(libraryName);
    libraryInfo.appendChild(libraryAddress);
    libraryBox.appendChild(libraryInfo);

    libraryBox.addEventListener("click", () => {
      console.log("Return button clicked for:", library.libraryUid);
      window.location.href = booksUrl + `?library_uid=${encodeURIComponent(library.libraryUid)}` + `&library_name=${encodeURIComponent(library.name)}`;
    });

    libraryContainer.appendChild(libraryBox);
  }
}


function dynamicLibraryBooks(books, document, bookContainer, libraryUid, idToken, username) {
  for (let i = 0; i < books.length; i++) {
    const book = books[i];

    const libraryBox = document.createElement("div");
    libraryBox.className = "library-box";

    const bookInfo = document.createElement("div");
    bookInfo.className = "book-info";

    const bookName = document.createElement("p");
    bookName.className = "book-title";
    bookName.textContent = (i + 1) + ". " + book.name;

    const bookAuthor = document.createElement("p");
    bookAuthor.className = "book-author";
    bookAuthor.textContent = "Author: " + book.author;

    const bookGenre = document.createElement("p");
    bookGenre.className = "book-genre";
    bookGenre.textContent = "Genre: " + book.genre;

    const bookAvailable = document.createElement("p");
    bookAvailable.textContent = "Available Left: " + book.availableCount;

    const bookCondition = document.createElement("p");
    bookCondition.className = "status-value";
    bookCondition.textContent = "Condition: " + book.condition;

    bookInfo.appendChild(bookName);
    bookInfo.appendChild(bookAuthor);
    bookInfo.appendChild(bookGenre);
    bookInfo.appendChild(bookAvailable);
    bookInfo.appendChild(bookCondition);

    const bookPicture = document.createElement("div");
    bookPicture.className = "book-picture";

    libraryBox.appendChild(bookInfo);
    libraryBox.appendChild(bookPicture);

    // DIALOGS

    const rentDialog = document.createElement("dialog");
    const dialogBookTitle = document.createElement("p");
    dialogBookTitle.className = "book-title"
    const dialogBookAuthor = document.createElement("p");

    const rentButton = document.createElement("button");
    rentButton.className = "rent-button";
    rentButton.textContent = "Rent";

    const cancelButton = document.createElement("button");
    cancelButton.className = "cancel-button";
    cancelButton.textContent = "Cancel";

    rentDialog.appendChild(dialogBookTitle);
    rentDialog.appendChild(dialogBookAuthor);
    rentDialog.appendChild(rentButton);
    rentDialog.appendChild(cancelButton);

    const rentResultDialog = document.getElementById("rent-result-dialog");
    const rentResult = document.getElementById("rent-result");
    const closeButton = document.getElementById("close-button");

    libraryBox.addEventListener("click", () => {
      console.log("Return button clicked for:", book.bookUid);
      dialogBookTitle.textContent = book.name;
      dialogBookAuthor.textContent = "by " + book.author;
      rentDialog.showModal();
    });
    rentButton.addEventListener("click", () => {
      rentDialog.close();
      rentResultDialog.showModal();
      rentBook(idToken, username, book.bookUid, libraryUid)
        .then(data => {
          if (!data.errors) {
            rentResult.textContent = "Successfully rented '" + data.book.name + "'!\nPlease return till " + data.tillDate;
            console.log('Response data:', data);
          }
          else {
            console.log('Error');
            rentResult.textContent = "Unable to rent this book.";
          }
        })
        .catch(error => {
          console.log('Error');
          rentResult.textContent = "Unable to rent this book.";
        });
    });
    cancelButton.addEventListener("click", () => {
      rentDialog.close();
    });
    closeButton.addEventListener("click", () => {
      rentResultDialog.close();
      location.reload();
    });
    bookContainer.appendChild(libraryBox);
    bookContainer.appendChild(rentDialog);
  }
}

async function initHeader(document, index_url, libraries_url) {
  if (!(checkCookie('id_token') && checkCookie('refresh_token'))) {
    window.location.href = index_url;
  }

  document.getElementById("logout-button").addEventListener("click", function () {
    deleteCookie('id_token');
    deleteCookie('refresh_token');
    window.location.href = index_url;
  });

  const searchButton = document.getElementById("search-button");
  const searchInput = document.getElementById("search-input");

  searchButton.addEventListener("click", function () {
    const cityName = searchInput.value.trim();
    const validCityNameRegex = /^[\-a-zA-Zа-яА-ЯёЁ\s]+$/; // Regular expression to allow only letters and spaces

    if (cityName !== "" && validCityNameRegex.test(cityName)) {
      window.location.href = libraries_url + `?city=${encodeURIComponent(cityName)}`;
    } else {
      // error message?
    }
  });

  const idToken = getCookie('id_token');
  const validationResponse = await validateToken(idToken);
  const username = validationResponse.payload.username;

  if ('error' in validationResponse) {
    deleteCookie('id_token');
    deleteCookie('refresh_token');
    window.location.href = index_url;
  } else {
    const usernameElement = document.getElementById('header-username');
    usernameElement.textContent = username + " | ";

    const avatarPlaceholder = document.getElementById('avatar-placeholder');
    avatarPlaceholder.textContent = username[0]

    const starCountElement = document.getElementById('star-count');

    data = await fetchUserRating(idToken, username);
    starCountElement.textContent = data.stars + " stars";
  }
}

async function initProfile(document) {

  const idToken = getCookie('id_token');
  const validationResponse = await validateToken(idToken);
  const username = validationResponse.payload.username;

  const bookContainer = document.getElementById("book-container");
  const historyContainer = document.getElementById("history-book-container");

  books = await fetchUserReservations(idToken, username);
  const rentedBooks = books.filter(book => book.status === "RENTED");
  const notRentedBooks = books.filter(book => book.status !== "RENTED");
  rentedBooks.sort((a, b) => new Date(b.startDate) - new Date(a.startDate));
  notRentedBooks.sort((a, b) => new Date(b.startDate) - new Date(a.startDate));

  dynamicBooks(rentedBooks, document, bookContainer, idToken, username);
  dynamicBooks(notRentedBooks, document, historyContainer, idToken, username);

  const rentedBooksTitle = document.getElementById("rented-books-title");
  rentedBooksTitle.textContent = "Rented Books (" + rentedBooks.length + ")"
  const returnedBooksTitle = document.getElementById("returned-books-title");
  returnedBooksTitle.textContent = "Returned Books (" + notRentedBooks.length + ")"
}

async function initLibraries(document, booksUrl) {
  const idToken = getCookie('id_token');
  const validationResponse = await validateToken(idToken);
  const username = validationResponse.payload.username;

  const queryParams = new URLSearchParams(window.location.search);
  const cityName = queryParams.get('city');
  if (!cityName) {
    window.history.back();
  }

  const cityNameHeading = document.getElementById("city-name-heading");
  cityNameHeading.textContent = `${cityName} Libraries`;

  const data = await fetchCityLibraries(idToken, username, cityName, 0, 250);
  const libraries = data.items;
  const libraryContainer = document.getElementById("library-container");
  dynamicLibraries(libraries, document, libraryContainer, booksUrl)
}

async function initBooks(document) {
  const idToken = getCookie('id_token');
  const validationResponse = await validateToken(idToken);
  const username = validationResponse.payload.username;

  const queryParams = new URLSearchParams(window.location.search);
  const libraryUid = queryParams.get('library_uid');
  const libraryName = queryParams.get('library_name');
  if ((!libraryUid) || (!libraryName)) {
    window.history.back();
  }

  const libraryNameHeading = document.getElementById("library-name-heading");
  libraryNameHeading.textContent = libraryName;

  const data = await fetchLibraryBooks(idToken, username, libraryUid, 0, 250);
  const books = data.items;
  const bookContainer = document.getElementById("book-container");
  dynamicLibraryBooks(books, document, bookContainer, libraryUid, idToken, username)
}

// ############################# REQUESTS ################################

function returnBook(idToken, username, reservationUid, condition) {
  const apiUrl = new URL('/api/v1/reservations', gatewayUrl);

  const headers = {
    'X-User-Name': username,
    'X-Id-Token': idToken,
  }

  const requestBody = {
    "condition": condition,
    "date": generateTodayDate()
  }

  const requestUrl = `${apiUrl}/${reservationUid}/return`;

  return fetch(requestUrl, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(requestBody)
  })
    .then(response => {
      return response;
    })
    .then(data => {
      return data;
    })
    .catch(error => {
      console.error('Fetch error:', error);
      throw error;
    });
}

function rentBook(idToken, username, bookUid, libraryUid) {
  const apiUrl = new URL('/api/v1/reservations', gatewayUrl);

  const headers = {
    'X-User-Name': username,
    'X-Id-Token': idToken,
  }

  const requestBody = {
    "bookUid": bookUid,
    "libraryUid": libraryUid,
    "tillDate": generateDateOneMonthFromNow()
  }

  return fetch(apiUrl, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(requestBody)
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      return data;
    })
    .catch(error => {
      console.error('Fetch error:', error);
      throw error;
    });
}

function fetchLibraryBooks(idToken, username, libraryUid, page, size) {
  const apiUrl = new URL('/api/v1/libraries', gatewayUrl);
  const queryParams = new URLSearchParams({
    showAll: false,
    page: page,
    size: size
  });

  const requestUrl = `${apiUrl}/${libraryUid}/books?${queryParams.toString()}`;

  return fetch(requestUrl, {
    method: "GET",
    headers: {
      'X-User-Name': username,
      'X-Id-Token': idToken,
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      return data;
    })
    .catch(error => {
      console.error('Fetch error:', error);
      throw error;
    });
}

function fetchCityLibraries(idToken, username, city, page, size) {
  const apiUrl = new URL('/api/v1/libraries', gatewayUrl);
  const queryParams = new URLSearchParams({
    city: city,
    page: page,
    size: size
  });

  const requestUrl = `${apiUrl}?${queryParams.toString()}`;

  return fetch(requestUrl, {
    method: "GET",
    headers: {
      'X-User-Name': username,
      'X-Id-Token': idToken,
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      return data;
    })
    .catch(error => {
      console.error('Fetch error:', error);
      throw error;
    });
}

function fetchUserReservations(idToken, username) {
  const apiUrl = new URL('/api/v1/reservations', gatewayUrl);

  return fetch(apiUrl, {
    method: 'GET',
    headers: {
      'X-User-Name': username,
      'X-Id-Token': idToken,
    },
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      return data;
    })
    .catch(error => {
      console.error('Fetch error:', error);
      throw error;
    });
}

function fetchUserRating(idToken, username) {
  const apiUrl = new URL('/api/v1/rating', gatewayUrl);

  return fetch(apiUrl, {
    method: 'GET',
    headers: {
      'X-User-Name': username,
      'X-Id-Token': idToken,
    },
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      return data;
    })
    .catch(error => {
      console.error('Fetch error:', error);
      throw error;
    });
}
