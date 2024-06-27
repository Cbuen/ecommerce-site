var user_name = "chris"
var pass_word = "123"


async function displayUsers() {
    const response = await fetch('https://fakestoreapi.com/users');
    const users = await response.json();

    // actual creation of the usernames array I DIDNT KNOW THIS
    const usernames = users.map(user => user.username);

    return usernames
}



async function findUserBy
(usernameToFind) {
    try {
      // Fetch all users from the API
      const response = await fetch('https://fakestoreapi.com/users');
      const users = await response.json();
  
      // Use find() to get the user with the matching username
      const user = users.find(user => user.username === usernameToFind);
  
      if (user) {
        console.log('User found:', user);
        return user;
      } else {
        console.log('User not found');
        return null;
      }
    } catch (error) {
      console.error('Error finding user:', error);
      return null;
    }
  }