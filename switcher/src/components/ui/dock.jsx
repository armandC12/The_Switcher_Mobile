import {
    motion,
    useMotionValue,
    useSpring,
    useTransform,
    AnimatePresence,
} from 'framer-motion';
import {
    Children,
    cloneElement,
    createContext,
    useContext,
    useMemo,
    useRef,
    useEffect,
    useState,
} from 'react';
import { cn } from '@/lib/utils';

const DOCK_HEIGHT = 128;
const DEFAULT_MAGNIFICATION = 100; // Increased magnification for bigger cards
const DEFAULT_DISTANCE = 150;
const DEFAULT_PANEL_HEIGHT = 64;

const DockContext = createContext(undefined);

function DockProvider({ children, value }) {
    return <DockContext.Provider value={value}>{children}</DockContext.Provider>;
}

function useDock() {
    const context = useContext(DockContext);
    if (!context) {
        throw new Error('useDock must be used within a DockProvider');
    }
    return context;
}

function Dock({
    children,
    className,
    spring = { mass: 0.1, stiffness: 150, damping: 12 },
    magnification = DEFAULT_MAGNIFICATION,
    distance = DEFAULT_DISTANCE,
    panelHeight = DEFAULT_PANEL_HEIGHT,
}) {
    const mouseX = useMotionValue(Infinity);
    const isHovered = useMotionValue(0);

    const maxHeight = useMemo(() => {
        return Math.max(DOCK_HEIGHT, magnification + magnification / 2 + 4);
    }, [magnification]);

    const heightRow = useTransform(isHovered, [0, 1], [panelHeight, maxHeight]);
    const height = useSpring(heightRow, spring);

    return (
        <motion.div
            style={{
                height: '100%',
                width: '100%',
            }}
            className="flex items-end overflow-x-auto"
        >
            <motion.div
                onMouseMove={({ pageX }) => {
                    isHovered.set(1);
                    mouseX.set(pageX);
                }}
                onMouseLeave={() => {
                    isHovered.set(0);
                    mouseX.set(Infinity);
                }}
                className={cn(
                    'm-auto flex w-full h-full gap-4 justify-center rounded-2xl', // Added justify-center
                    className
                )}
                style={{ height: panelHeight }}
                role="toolbar"
                aria-label="Other player dock"
            >
                <DockProvider value={{ mouseX, spring, distance, magnification }}>
                    {children}
                </DockProvider>
            </motion.div>
        </motion.div>
    );
}

function DockItem({ children, className }) {
    const ref = useRef(null);

    const { distance, magnification, mouseX, spring } = useDock();

    const isHovered = useMotionValue(0);

    const mouseDistance = useTransform(mouseX, (val) => {
        const domRect = ref.current?.getBoundingClientRect() ?? { x: 0, width: 0 };
        return val - domRect.x - domRect.width / 2;
    });

    // const widthTransform = useTransform(
    //     mouseDistance,
    //     [-distance, 0, distance],
    //     [50, magnification, 50] // Increased card width
    // );

    const widthTransform = useTransform(
        mouseDistance,
        [-distance, 0, distance],
        [70, magnification * 1.5, 100] // Increased base width and magnification for bigger cards
    );

    const width = useSpring(widthTransform, spring);

    return (
        <motion.div
            ref={ref}
            style={{ width }}
            onHoverStart={() => isHovered.set(1)}
            onHoverEnd={() => isHovered.set(0)}
            onFocus={() => isHovered.set(1)}
            onBlur={() => isHovered.set(0)}
            className={cn(
                'relative inline-flex items-center justify-center',
                className
            )}
            tabIndex={0}
            role="button"
            aria-haspopup="true"
        >
            {Children.map(children, (child) =>
                cloneElement(child, { width, isHovered })
            )}
        </motion.div>
    );
}

function DockLabel({ children, className, ...rest }) {
    const restProps = rest;
    const isHovered = restProps['isHovered'];
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const unsubscribe = isHovered.on('change', (latest) => {
            setIsVisible(latest === 1);
        });

        return () => unsubscribe();
    }, [isHovered]);

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, y: 0 }}
                    animate={{ opacity: 1, y: -10 }}
                    exit={{ opacity: 0, y: 0 }}
                    transition={{ duration: 0.2 }}
                    className={cn(
                        'absolute -top-6 left-1/2 w-fit whitespace-pre rounded-md px-2 py-0.5 text-xs ',
                        className
                    )}
                    role="tooltip"
                    style={{ x: '-50%' }}
                >
                    {children}
                </motion.div>
            )}
        </AnimatePresence>
    );
}

function DockIcon({ children, className, ...rest }) {
    const restProps = rest;
    const width = restProps['width'];

    const widthTransform = useTransform(width, (val) => val / 2);

    return (
        <motion.div
            style={{ width: widthTransform }}
            className={cn('flex items-center justify-center w-full h-full', className)}
        >
            {children}
        </motion.div>
    );
}

export { Dock, DockIcon, DockItem, DockLabel };
