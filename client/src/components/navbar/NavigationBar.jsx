import Cookies from "universal-cookie";
import PropTypes from "prop-types";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

/**
 * Top-level navigation bar with branding, page links, and an account dropdown.
 *
 * @param {Object} props
 * @param {boolean} props.loggedIn - Whether the current user is authenticated.
 * @returns {JSX.Element}
 */
const NavigationBar = ({loggedIn}) =>
{
    /**
     * Removes the auth token cookie, effectively logging the user out.
     */
    const logOut = () =>
    {
        const cookies = new Cookies();
        cookies.remove("token");
    };

    const menuItemClass = "block px-2 py-1.5 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground no-underline text-inherit transition-colors";

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 h-[52px] bg-[#2C2C2C] flex items-center px-4">
            <div className="flex items-center flex-1">
                <a href="/" className="flex items-center gap-2 text-white font-semibold text-lg no-underline mr-6">
                    <img src="/schedulo.png" alt="logo" className="h-7 w-7" />
                    Schedulo
                </a>
                <a href="/" className="text-white/80 hover:text-white text-sm mr-4 no-underline transition-colors">Dashboard</a>
                <a href="/about" className="text-white/80 hover:text-white text-sm no-underline transition-colors">About</a>
            </div>

            {loggedIn && (
                <DropdownMenu modal={false}>
                    <DropdownMenuTrigger className="text-white/80 hover:text-white text-sm transition-colors outline-none">
                        Account
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <a href="/profile" className={menuItemClass}>Settings</a>
                        <a href="/" onClick={logOut} className={menuItemClass}>Log out</a>
                    </DropdownMenuContent>
                </DropdownMenu>
            )}
        </nav>
    );
};

NavigationBar.propTypes = {
    loggedIn: PropTypes.bool.isRequired,
};

export default NavigationBar;
